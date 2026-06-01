"""
TUI Workflow Monitor
"""

import time
import threading
from typing import Dict, Any, Optional

from flowpilot.core.parser import WorkflowParser
from flowpilot.core.engine import WorkflowEngine
from flowpilot.models.workflow import Workflow, Task, Step, WorkflowStatus, TaskStatus


class WorkflowMonitor:
    """Terminal UI for workflow monitoring"""
    
    def __init__(self, workflow: Workflow, variables: Optional[Dict[str, Any]] = None):
        self.workflow = workflow
        self.variables = variables or {}
        self.engine: Optional[WorkflowEngine] = None
        self.running = False
        self.logs: list = []
        self.current_task: Optional[str] = None
        self.current_step: Optional[str] = None
    
    def run(self) -> bool:
        """Run workflow with TUI monitoring"""
        self.running = True
        
        # Print header
        self._print_header()
        
        # Setup engine with callbacks
        self.engine = WorkflowEngine(
            workflow=self.workflow,
            on_task_start=self._on_task_start,
            on_task_end=self._on_task_end,
            on_step_start=self._on_step_start,
            on_step_end=self._on_step_end,
            on_workflow_start=self._on_workflow_start,
            on_workflow_end=self._on_workflow_end,
        )
        
        # Run workflow
        try:
            success = self.engine.run(self.variables)
            return success
        except Exception as e:
            self._log(f"❌ Error: {e}", "error")
            return False
    
    def _print_header(self):
        """Print TUI header"""
        print("\n" + "=" * 70)
        print(f"🚀 FlowPilot Workflow Monitor")
        print(f"   Workflow: {self.workflow.name}")
        if self.workflow.description:
            print(f"   Description: {self.workflow.description}")
        print("=" * 70 + "\n")
    
    def _on_workflow_start(self, workflow: Workflow):
        """Called when workflow starts"""
        self._log(f"▶️  Workflow '{workflow.name}' started", "info")
    
    def _on_workflow_end(self, workflow: Workflow):
        """Called when workflow ends"""
        status_icon = "✅" if workflow.status == WorkflowStatus.SUCCESS else "❌"
        duration = workflow.duration
        duration_str = f"{duration:.2f}s" if duration else "N/A"
        
        print("\n" + "=" * 70)
        print(f"{status_icon} Workflow completed: {workflow.status.value.upper()}")
        print(f"   Duration: {duration_str}")
        
        # Task summary
        total = len(workflow.tasks)
        successful = sum(1 for t in workflow.tasks if t.status == TaskStatus.SUCCESS)
        failed = sum(1 for t in workflow.tasks if t.status == TaskStatus.FAILED)
        skipped = sum(1 for t in workflow.tasks if t.status == TaskStatus.SKIPPED)
        
        print(f"   Tasks: {successful} success, {failed} failed, {skipped} skipped (total: {total})")
        print("=" * 70 + "\n")
    
    def _on_task_start(self, task: Task):
        """Called when task starts"""
        self.current_task = task.name
        self._log(f"🔄 [{task.name}] Starting...", "task")
    
    def _on_task_end(self, task: Task):
        """Called when task ends"""
        status_icons = {
            TaskStatus.SUCCESS: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️",
            TaskStatus.CANCELLED: "🚫",
        }
        icon = status_icons.get(task.status, "❓")
        
        duration = task.duration
        duration_str = f" ({duration:.2f}s)" if duration else ""
        
        self._log(f"{icon} [{task.name}] {task.status.value.upper()}{duration_str}", "task")
        
        if task.error:
            error_preview = task.error[:200].replace('\n', ' ')
            self._log(f"   Error: {error_preview}", "error")
    
    def _on_step_start(self, step: Step):
        """Called when step starts"""
        self.current_step = step.name
        cmd_preview = step.command[:50] + "..." if len(step.command) > 50 else step.command
        self._log(f"   ▶️  {step.name}: {cmd_preview}", "step")
    
    def _on_step_end(self, step: Step, success: bool):
        """Called when step ends"""
        icon = "✓" if success else "✗"
        self._log(f"   {icon} {step.name}", "step")
    
    def _log(self, message: str, level: str = "info"):
        """Add log message"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append((level, log_entry))
        print(log_entry)
