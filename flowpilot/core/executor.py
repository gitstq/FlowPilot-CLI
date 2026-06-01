"""
Task Execution Engine
"""

import subprocess
import os
import time
import signal
import threading
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from ..models.workflow import Task, Step, WorkflowContext, TaskStatus


class TaskExecutor:
    """Execute workflow tasks and steps"""
    
    def __init__(self, context: WorkflowContext, 
                 on_step_start: Optional[Callable] = None,
                 on_step_end: Optional[Callable] = None,
                 on_task_start: Optional[Callable] = None,
                 on_task_end: Optional[Callable] = None):
        self.context = context
        self.on_step_start = on_step_start
        self.on_step_end = on_step_end
        self.on_task_start = on_task_start
        self.on_task_end = on_task_end
        self._cancelled = False
    
    def cancel(self):
        """Cancel execution"""
        self._cancelled = True
    
    def execute_task(self, task: Task) -> bool:
        """Execute a single task"""
        if self._cancelled:
            task.status = TaskStatus.CANCELLED
            return False
        
        # Check condition
        if task.condition and not self._evaluate_condition(task.condition):
            task.status = TaskStatus.SKIPPED
            return True
        
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        
        if self.on_task_start:
            self.on_task_start(task)
        
        try:
            success = True
            task.output = ""
            task.error = ""
            
            for step in task.steps:
                if self._cancelled:
                    task.status = TaskStatus.CANCELLED
                    return False
                
                step_success = self._execute_step(step, task)
                if not step_success and not step.ignore_error:
                    success = False
                    break
            
            task.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
            self.context.set_task_result(task.name, {
                "success": success,
                "output": task.output,
                "error": task.error,
            })
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.context.set_task_result(task.name, {
                "success": False,
                "error": str(e),
            })
        
        task.end_time = time.time()
        
        if self.on_task_end:
            self.on_task_end(task)
        
        return task.status == TaskStatus.SUCCESS
    
    def _execute_step(self, step: Step, task: Task) -> bool:
        """Execute a single step"""
        # Check condition
        if step.condition and not self._evaluate_condition(step.condition):
            return True
        
        if self.on_step_start:
            self.on_step_start(step)
        
        # Resolve template variables
        command = self.context.resolve_template(step.command)
        working_dir = step.working_dir
        if working_dir:
            working_dir = self.context.resolve_template(working_dir)
        
        # Prepare environment
        env = os.environ.copy()
        env.update(self.context.workflow.env)
        env.update(step.env)
        
        # Resolve env variables
        for key, value in env.items():
            env[key] = self.context.resolve_template(value)
        
        # Execute with retry logic
        attempt = 0
        max_attempts = step.retry + 1
        last_error = None
        
        while attempt < max_attempts:
            if self._cancelled:
                return False
            
            attempt += 1
            
            try:
                result = self._run_command(
                    command=command,
                    working_dir=working_dir,
                    env=env,
                    timeout=step.timeout,
                )
                
                if result['success']:
                    task.output += result['stdout']
                    if result['stderr']:
                        task.output += f"\n[stderr]: {result['stderr']}"
                    
                    if self.on_step_end:
                        self.on_step_end(step, True)
                    return True
                else:
                    last_error = result['stderr'] or result['stdout']
                    if attempt < max_attempts:
                        time.sleep(step.retry_delay)
                    
            except Exception as e:
                last_error = str(e)
                if attempt < max_attempts:
                    time.sleep(step.retry_delay)
        
        # All retries failed
        task.error += f"\nStep '{step.name}' failed after {attempt} attempts: {last_error}"
        
        if self.on_step_end:
            self.on_step_end(step, False)
        
        return False
    
    def _run_command(self, command: str, working_dir: Optional[str] = None,
                     env: Optional[Dict[str, str]] = None, 
                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """Run a shell command and return result"""
        cwd = Path(working_dir) if working_dir else Path.cwd()
        
        # Use shell=True for complex commands
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            env=env,
        )
        
        stdout_lines = []
        stderr_lines = []
        
        def read_stream(stream, lines):
            for line in iter(stream.readline, ''):
                lines.append(line)
            stream.close()
        
        stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, stdout_lines))
        stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, stderr_lines))
        
        stdout_thread.start()
        stderr_thread.start()
        
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            raise TimeoutError(f"Command timed out after {timeout} seconds")
        
        stdout_thread.join()
        stderr_thread.join()
        
        stdout = ''.join(stdout_lines)
        stderr = ''.join(stderr_lines)
        
        return {
            'success': process.returncode == 0,
            'returncode': process.returncode,
            'stdout': stdout,
            'stderr': stderr,
        }
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition expression"""
        # Resolve template variables first
        condition = self.context.resolve_template(condition)
        
        # Handle common condition patterns
        condition = condition.strip()
        
        # Check for env variable existence
        if condition.startswith('env.'):
            var_name = condition[4:]
            return bool(os.environ.get(var_name))
        
        # Check for task success
        if condition.startswith('tasks.'):
            parts = condition[6:].split('.')
            task_name = parts[0]
            task_result = self.context.get_task_result(task_name)
            if task_result is None:
                return False
            if len(parts) > 1 and parts[1] == 'success':
                return task_result.get('success', False)
            return bool(task_result)
        
        # Simple boolean evaluation
        if condition.lower() in ('true', 'yes', '1', 'on'):
            return True
        if condition.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Try to evaluate as Python expression
        try:
            # Create safe evaluation context
            eval_context = {
                'vars': self.context.workflow.vars,
                'env': dict(os.environ),
                'tasks': self.context.task_results,
            }
            return bool(eval(condition, {"__builtins__": {}}, eval_context))
        except:
            # If evaluation fails, treat as truthy string check
            return bool(condition)
