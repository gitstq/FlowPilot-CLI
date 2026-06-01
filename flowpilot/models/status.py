"""
Status Enums and Utilities
"""

from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    
    @property
    def icon(self) -> str:
        icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.RUNNING: "🔄",
            TaskStatus.SUCCESS: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.SKIPPED: "⏭️",
            TaskStatus.CANCELLED: "🚫",
        }
        return icons.get(self, "❓")
    
    @property
    def color(self) -> str:
        colors = {
            TaskStatus.PENDING: "yellow",
            TaskStatus.RUNNING: "blue",
            TaskStatus.SUCCESS: "green",
            TaskStatus.FAILED: "red",
            TaskStatus.SKIPPED: "dim",
            TaskStatus.CANCELLED: "red",
        }
        return colors.get(self, "white")


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    @property
    def icon(self) -> str:
        icons = {
            WorkflowStatus.PENDING: "⏳",
            WorkflowStatus.RUNNING: "🔄",
            WorkflowStatus.SUCCESS: "✅",
            WorkflowStatus.FAILED: "❌",
            WorkflowStatus.CANCELLED: "🚫",
        }
        return icons.get(self, "❓")
    
    @property
    def color(self) -> str:
        colors = {
            WorkflowStatus.PENDING: "yellow",
            WorkflowStatus.RUNNING: "blue",
            WorkflowStatus.SUCCESS: "green",
            WorkflowStatus.FAILED: "red",
            WorkflowStatus.CANCELLED: "red",
        }
        return colors.get(self, "white")


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    
    @property
    def icon(self) -> str:
        icons = {
            StepStatus.PENDING: "⏳",
            StepStatus.RUNNING: "🔄",
            StepStatus.SUCCESS: "✅",
            StepStatus.FAILED: "❌",
            StepStatus.SKIPPED: "⏭️",
        }
        return icons.get(self, "❓")
