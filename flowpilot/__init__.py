"""
FlowPilot-CLI - Lightweight Terminal Workflow Orchestration Engine
轻量级终端工作流编排引擎

A zero-dependency, YAML-driven workflow automation tool for developers.
"""

__version__ = "1.0.0"
__author__ = "FlowPilot Team"
__license__ = "MIT"

from .core.engine import WorkflowEngine
from .core.parser import WorkflowParser
from .core.executor import TaskExecutor
from .models.workflow import Workflow, Task, Step

__all__ = [
    "WorkflowEngine",
    "WorkflowParser", 
    "TaskExecutor",
    "Workflow",
    "Task",
    "Step",
]
