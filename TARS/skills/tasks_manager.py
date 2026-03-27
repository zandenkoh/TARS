"""Manager for daily tasks stored as JSON."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from loguru import logger

# Constants
TASK_STATUS = Literal["pending", "done", "skipped"]
DEFAULT_TASKS_DIR = "~/.TARS/workspace/tasks"

class TasksManager:
    """Manages loading, saving, and updating daily task JSON files."""

    def __init__(self, workspace_path: Path | str | None = None):
        if workspace_path:
            self.tasks_dir = Path(workspace_path) / "tasks"
        else:
            self.tasks_dir = Path(os.path.expanduser(DEFAULT_TASKS_DIR))
        
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, date_str: str) -> Path:
        """Get the file path for a specific date (YYYY-MM-DD)."""
        return self.tasks_dir / f"daily_{date_str}.json"

    def load_tasks(self, date_str: str | None = None) -> dict[str, Any] | None:
        """Load tasks for the given date, or today if None."""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        path = self._get_path(date_str)
        if not path.exists():
            return None
        
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception) as e:
            logger.error("Failed to load tasks for {}: {}", date_str, e)
            return None

    def save_tasks(self, tasks_data: dict[str, Any]) -> bool:
        """Save tasks data to disk."""
        date_str = tasks_data.get("date")
        if not date_str:
            logger.error("Cannot save tasks without a date")
            return False
        
        path = self._get_path(date_str)
        try:
            path.write_text(json.dumps(tasks_data, indent=2, ensure_ascii=False), encoding="utf-8")
            return True
        except Exception as e:
            logger.error("Failed to save tasks for {}: {}", date_str, e)
            return False

    def update_task_status(self, date_str: str, task_id: str, status: TASK_STATUS) -> bool:
        """Update a specific task's status."""
        data = self.load_tasks(date_str)
        if not data:
            return False
        
        updated = False
        for task in data.get("tasks", []):
            if task.get("id") == task_id:
                task["status"] = status
                updated = True
                break
        
        if updated:
            return self.save_tasks(data)
        
        return False

    def render_task_list(self, tasks_data: dict[str, Any]) -> str:
        """Render the task list as a formatted string."""
        date_str = tasks_data.get("date", "Today")
        tasks = tasks_data.get("tasks", [])
        summary = tasks_data.get("summary", "")

        lines = [f"📅 *Daily Tasks - {date_str}*"]
        if summary:
            lines.append(f"_{summary}_")
        lines.append("")

        if not tasks:
            lines.append("No tasks for today. Use `/tasks` to generate some!")
            return "\n".join(lines)

        for i, t in enumerate(tasks, 1):
            status_icon = "⏳" # pending
            if t.get("status") == "done":
                status_icon = "✅"
            elif t.get("status") == "skipped":
                status_icon = "⏭"
            
            title = t.get("title", "No Title")
            priority = t.get("priority", "medium").upper()
            
            lines.append(f"{i}. {status_icon} *{title}* (`{priority}`)")
            if t.get("description"):
                lines.append(f"   _{t.get('description')}_")
        
        return "\n".join(lines)

    def format_telegram_markup(self, tasks_data: dict[str, Any]) -> dict:
        """Build the Telegram InlineKeyboardMarkup structure."""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        date_str = tasks_data.get("date")
        tasks = tasks_data.get("tasks", [])
        
        keyboard = []
        
        # Add buttons for each pending task
        for t in tasks:
            if t.get("status") == "pending":
                task_id = t.get("id")
                title = t.get("title", "Task")
                # Truncate title for button if needed
                if len(title) > 20:
                    title = title[:17] + "..."
                
                row = [
                    InlineKeyboardButton(f"✅ Done: {title}", callback_data=f"task:done:{date_str}:{task_id}"),
                    InlineKeyboardButton("⏭ Skip", callback_data=f"task:skip:{date_str}:{task_id}")
                ]
                keyboard.append(row)
        
        # Bottom row for management
        mgmt_row = [
            InlineKeyboardButton("➕ Add", callback_data=f"task:add:{date_str}"),
            InlineKeyboardButton("📅 Refresh", callback_data=f"task:refresh:{date_str}"),
            InlineKeyboardButton("📋 All", callback_data=f"task:view_all:{date_str}"),
            InlineKeyboardButton("⚙️ Time", callback_data=f"task:time_menu:{date_str}")
        ]
        keyboard.append(mgmt_row)
        
        return InlineKeyboardMarkup(keyboard)

    def format_time_selection_markup(self, date_str: str) -> dict:
        """Build the Telegram InlineKeyboardMarkup for time selection."""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        times = ["06:00", "07:00", "08:00", "09:00", "10:00"]
        keyboard = []
        for i in range(0, len(times), 2):
            row = []
            row.append(InlineKeyboardButton(times[i], callback_data=f"task:set_time:{times[i].replace(':', '-')}"))
            if i + 1 < len(times):
                row.append(InlineKeyboardButton(times[i+1], callback_data=f"task:set_time:{times[i+1].replace(':', '-')}"))
            keyboard.append(row)
        
        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"task:refresh:{date_str}")])
        
        return InlineKeyboardMarkup(keyboard)

# Global singleton or instance if needed
# For now, we'll instantiate it in the channel/skill as needed.
