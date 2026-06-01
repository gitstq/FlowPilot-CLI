"""
Workflow Execution Engine
"""

import time
from typing import Optional, List, Dict, Any, Callable
from collections import deque

from ..models.workflow import Workflow, Task, WorkflowContext, WorkflowStatus, TaskStatus
from .executor import TaskExecutor


class WorkflowEngine:
    """Main workflow execution engine"""
    
    def __init__(self, workflow: Workflow,
                 on_task_start: Optional[Callable] = None,
                 on_task_end: Optional[Callable] = None,
                 on_step_start: Optional[Callable] = None,
                 on_step_end: Optional[Callable] = None,
                 on_workflow_start: Optional[Callable] = None,
                 on_workflow_end: Optional[Callable] = None):
        self.workflow = workflow
        self.context = WorkflowContext(workflow=workflow)
        self.on_task_start = on_task_start
        self.on_task_end = on_task_end
        self.on_step_start = on_step_start
        self.on_step_end = on_step_end
        self.on_workflow_start = on_workflow_start
        self.on_workflow_end = on_workflow_end
        self._cancelled = False
        self._executor: Optional[TaskExecutor] = None
    
    def run(self, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Execute the complete workflow"""
        if variables:
            for key, value in variables.items():
                self.context.set_variable(key, value)
        
        self.workflow.status = WorkflowStatus.RUNNING
        self.workflow.start_time = time.time()
        
        if self.on_workflow_start:
            self.on_workflow_start(self.workflow)
        
        try:
            success = self._execute_workflow()
            self.workflow.status = WorkflowStatus.SUCCESS if success else WorkflowStatus.FAILED
        except Exception as e:
            self.workflow.status = WorkflowStatus.FAILED
            success = False
        
        self.workflow.end_time = time.time()
        
        if self.on_workflow_end:
            self.on_workflow_end(self.workflow)
        
        return success
    
    def cancel(self):
        """Cancel workflow execution"""
        self._cancelled = True
        if self._executor:
            self._executor.cancel()
    
    def _execute_workflow(self) -> bool:
        """Execute workflow tasks respecting dependencies"""
        # Build dependency graph
        pending_tasks = set(task.name for task in self.workflow.tasks)
        completed_tasks = set()
        failed_tasks = set()
        
        self._executor = TaskExecutor(
            context=self.context,
            on_step_start=self.on_step_start,
            on_step_end=self.on_step_end,
            on_task_start=self.on_task_start,
            on_task_end=self.on_task_end,
        )
        
        while pending_tasks:
            if self._cancelled:
                self.workflow.status = WorkflowStatus.CANCELLED
                return False
            
            # Find tasks that are ready to run (all dependencies completed)
            ready_tasks = []
            for task_name in pending_tasks:
                task = self.workflow.get_task(task_name)
                if not task:
                    continue
                
                deps_satisfied = all(
                    dep in completed_tasks 
                    for dep in task.depends_on
                )
                
                if deps_satisfied:
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Check if there are remaining tasks with unmet dependencies
                remaining_deps = set()
                for task_name in pending_tasks:
                    task = self.workflow.get_task(task_name)
                    if task:
                        for dep in task.depends_on:
                            if dep not in completed_tasks:
                                remaining_deps.add(dep)
                
                if remaining_deps:
                    raise ValueError(f"Dependency resolution failed. Missing or failed tasks: {remaining_deps}")
                break
            
            # Execute ready tasks
            for task in ready_tasks:
                if self._cancelled:
                    return False
                
                success = self._executor.execute_task(task)
                pending_tasks.remove(task.name)
                
                if success:
                    completed_tasks.add(task.name)
                else:
                    failed_tasks.add(task.name)
                    # Continue with other tasks unless this is a critical failure
        
        return len(failed_tasks) == 0
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary"""
        total_tasks = len(self.workflow.tasks)
        successful_tasks = sum(1 for t in self.workflow.tasks if t.status == TaskStatus.SUCCESS)
        failed_tasks = sum(1 for t in self.workflow.tasks if t.status == TaskStatus.FAILED)
        skipped_tasks = sum(1 for t in self.workflow.tasks if t.status == TaskStatus.SKIPPED)
        
        return {
            "workflow_name": self.workflow.name,
            "status": self.workflow.status.value,
            "duration": self.workflow.duration,
            "total_tasks": total_tasks,
            "successful": successful_tasks,
            "failed": failed_tasks,
            "skipped": skipped_tasks,
            "tasks": [
                {
                    "name": t.name,
                    "status": t.status.value,
                    "duration": t.duration,
                    "output": t.output[:500] if t.output else "",  # Truncate output
                    "error": t.error[:500] if t.error else "",
                }
                for t in self.workflow.tasks
            ]
        }
