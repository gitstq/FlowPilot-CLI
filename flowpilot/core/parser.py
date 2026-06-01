"""
Workflow YAML Parser
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..models.workflow import Workflow, Task, Step


class WorkflowParser:
    """Parse YAML workflow definitions"""
    
    @staticmethod
    def parse_file(file_path: str) -> Workflow:
        """Parse a workflow from YAML file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return WorkflowParser.parse_string(content)
    
    @staticmethod
    def parse_string(content: str) -> Workflow:
        """Parse a workflow from YAML string"""
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        
        if not isinstance(data, dict):
            raise ValueError("Workflow must be a YAML object")
        
        return WorkflowParser._parse_workflow(data)
    
    @staticmethod
    def _parse_workflow(data: Dict[str, Any]) -> Workflow:
        """Parse workflow from dictionary"""
        name = data.get('name')
        if not name:
            raise ValueError("Workflow must have a 'name' field")
        
        workflow = Workflow(
            name=name,
            version=data.get('version', '1.0'),
            description=data.get('description'),
            env=data.get('env', {}),
            vars=data.get('vars', {}),
            triggers=data.get('triggers', []),
        )
        
        # Parse tasks
        tasks_data = data.get('tasks', {})
        if isinstance(tasks_data, dict):
            for task_name, task_data in tasks_data.items():
                task = WorkflowParser._parse_task(task_name, task_data)
                workflow.tasks.append(task)
        elif isinstance(tasks_data, list):
            for task_data in tasks_data:
                task_name = task_data.get('name')
                if not task_name:
                    raise ValueError("Task must have a 'name' field")
                task = WorkflowParser._parse_task(task_name, task_data)
                workflow.tasks.append(task)
        
        return workflow
    
    @staticmethod
    def _parse_task(name: str, data: Dict[str, Any]) -> Task:
        """Parse a task from dictionary"""
        steps_data = data.get('steps', [])
        steps = []
        
        for step_data in steps_data:
            step = WorkflowParser._parse_step(step_data)
            steps.append(step)
        
        # Handle single step shorthand
        if 'run' in data:
            step = Step(
                name=data.get('name', f"step_{len(steps) + 1}"),
                command=data['run'],
                description=data.get('description'),
                working_dir=data.get('working_dir'),
                env=data.get('env', {}),
                timeout=data.get('timeout'),
                retry=data.get('retry', 0),
                retry_delay=data.get('retry_delay', 1),
                ignore_error=data.get('ignore_error', False),
                condition=data.get('if'),
            )
            steps.append(step)
        
        depends_on = data.get('depends_on', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        
        return Task(
            name=name,
            description=data.get('description'),
            steps=steps,
            depends_on=depends_on,
            condition=data.get('if'),
            parallel=data.get('parallel', False),
            timeout=data.get('timeout'),
        )
    
    @staticmethod
    def _parse_step(data: Dict[str, Any]) -> Step:
        """Parse a step from dictionary"""
        if isinstance(data, str):
            return Step(name="command", command=data)
        
        name = data.get('name', 'step')
        command = data.get('run') or data.get('command')
        
        if not command:
            raise ValueError(f"Step '{name}' must have a 'run' or 'command' field")
        
        return Step(
            name=name,
            command=command,
            description=data.get('description'),
            working_dir=data.get('working_dir'),
            env=data.get('env', {}),
            timeout=data.get('timeout'),
            retry=data.get('retry', 0),
            retry_delay=data.get('retry_delay', 1),
            ignore_error=data.get('ignore_error', False),
            condition=data.get('if'),
        )
    
    @staticmethod
    def validate_workflow(workflow: Workflow) -> List[str]:
        """Validate a workflow and return list of errors"""
        errors = []
        
        # Check for duplicate task names
        task_names = [t.name for t in workflow.tasks]
        if len(task_names) != len(set(task_names)):
            errors.append("Duplicate task names found")
        
        # Check for circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_name: str) -> bool:
            visited.add(task_name)
            rec_stack.add(task_name)
            
            task = workflow.get_task(task_name)
            if task:
                for dep in task.depends_on:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(task_name)
            return False
        
        for task in workflow.tasks:
            if task.name not in visited:
                if has_cycle(task.name):
                    errors.append(f"Circular dependency detected involving task '{task.name}'")
        
        # Check for missing dependencies
        for task in workflow.tasks:
            for dep in task.depends_on:
                if not workflow.get_task(dep):
                    errors.append(f"Task '{task.name}' depends on non-existent task '{dep}'")
        
        return errors
