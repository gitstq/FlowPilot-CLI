"""
TUI UI Components
"""

from typing import List, Tuple, Optional
from flowpilot.models.workflow import Task, TaskStatus


class TaskPanel:
    """Display task execution status"""
    
    def __init__(self, width: int = 60):
        self.width = width
        self.tasks: List[Task] = []
    
    def update_tasks(self, tasks: List[Task]):
        """Update task list"""
        self.tasks = tasks
    
    def render(self) -> str:
        """Render task panel as string"""
        lines = []
        lines.append("┌" + "─" * (self.width - 2) + "┐")
        lines.append("│ Tasks" + " " * (self.width - 9) + "│")
        lines.append("├" + "─" * (self.width - 2) + "┤")
        
        for task in self.tasks:
            status_icon = task.status.icon
            name = task.name[:self.width - 10]
            padding = " " * (self.width - len(name) - 8)
            lines.append(f"│ {status_icon} {name}{padding}│")
        
        lines.append("└" + "─" * (self.width - 2) + "┘")
        return "\n".join(lines)


class LogPanel:
    """Display execution logs"""
    
    def __init__(self, width: int = 60, height: int = 15):
        self.width = width
        self.height = height
        self.logs: List[Tuple[str, str]] = []
    
    def add_log(self, message: str, level: str = "info"):
        """Add a log entry"""
        # Truncate message to fit width
        max_len = self.width - 4
        if len(message) > max_len:
            message = message[:max_len - 3] + "..."
        
        self.logs.append((level, message))
        
        # Keep only recent logs
        if len(self.logs) > self.height:
            self.logs = self.logs[-self.height:]
    
    def render(self) -> str:
        """Render log panel as string"""
        lines = []
        lines.append("┌" + "─" * (self.width - 2) + "┐")
        lines.append("│ Logs" + " " * (self.width - 8) + "│")
        lines.append("├" + "─" * (self.width - 2) + "┤")
        
        # Fill with logs
        for level, message in self.logs:
            padding = " " * (self.width - len(message) - 4)
            lines.append(f"│ {message}{padding}│")
        
        # Fill remaining space
        remaining = self.height - len(self.logs)
        for _ in range(remaining):
            lines.append("│" + " " * (self.width - 2) + "│")
        
        lines.append("└" + "─" * (self.width - 2) + "┘")
        return "\n".join(lines)


class StatusBar:
    """Display workflow status bar"""
    
    def __init__(self, width: int = 60):
        self.width = width
        self.workflow_name = ""
        self.status = "idle"
        self.progress = 0.0
    
    def update(self, name: str, status: str, progress: float):
        """Update status"""
        self.workflow_name = name
        self.status = status
        self.progress = max(0.0, min(1.0, progress))
    
    def render(self) -> str:
        """Render status bar"""
        # Progress bar
        bar_width = 20
        filled = int(self.progress * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Status text
        status_text = f"{self.workflow_name} | {self.status} | {bar} {int(self.progress * 100)}%"
        
        if len(status_text) > self.width - 2:
            status_text = status_text[:self.width - 5] + "..."
        
        padding = " " * (self.width - len(status_text) - 2)
        
        return f"│{status_text}{padding}│"
