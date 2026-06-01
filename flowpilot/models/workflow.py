"""
Workflow Data Models
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import time


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Step:
    """A single step in a task"""
    name: str
    command: str
    description: Optional[str] = None
    working_dir: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    timeout: Optional[int] = None
    retry: int = 0
    retry_delay: int = 1
    ignore_error: bool = False
    condition: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "command": self.command,
            "description": self.description,
            "working_dir": self.working_dir,
            "env": self.env,
            "timeout": self.timeout,
            "retry": self.retry,
            "retry_delay": self.retry_delay,
            "ignore_error": self.ignore_error,
            "condition": self.condition,
        }


@dataclass
class Task:
    """A task containing multiple steps"""
    name: str
    steps: List[Step]
    description: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    parallel: bool = False
    timeout: Optional[int] = None
    
    # Runtime fields
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    output: str = ""
    error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "depends_on": self.depends_on,
            "condition": self.condition,
            "parallel": self.parallel,
            "timeout": self.timeout,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.output,
            "error": self.error,
        }
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class Workflow:
    """Complete workflow definition"""
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    vars: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Runtime fields
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "env": self.env,
            "vars": self.vars,
            "triggers": self.triggers,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_task(self, name: str) -> Optional[Task]:
        for task in self.tasks:
            if task.name == name:
                return task
        return None


@dataclass
class WorkflowContext:
    """Context passed during workflow execution"""
    workflow: Workflow
    variables: Dict[str, Any] = field(default_factory=dict)
    task_results: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    
    def set_variable(self, name: str, value: Any):
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)
    
    def set_task_result(self, task_name: str, result: Any):
        self.task_results[task_name] = result
    
    def get_task_result(self, task_name: str) -> Any:
        return self.task_results.get(task_name)
    
    def resolve_template(self, template: str) -> str:
        """Resolve variable templates like ${{ variable }}"""
        import re
        
        def replace_var(match):
            var_path = match.group(1).strip()
            parts = var_path.split('.')
            
            if len(parts) == 1:
                # Simple variable
                return str(self.variables.get(var_path, match.group(0)))
            elif parts[0] == "vars":
                return str(self.workflow.vars.get(parts[1], match.group(0)))
            elif parts[0] == "env":
                import os
                return os.environ.get(parts[1], match.group(0))
            elif parts[0] == "tasks":
                task_result = self.task_results.get(parts[1], {})
                if len(parts) > 2:
                    return str(task_result.get(parts[2], match.group(0)))
                return str(task_result)
            
            return match.group(0)
        
        pattern = r'\$\{\{\s*([^}]+)\s*\}\}'
        return re.sub(pattern, replace_var, template)
