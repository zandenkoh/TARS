---
name: tasks
description: Manage your daily task list with interactive buttons in Telegram.
always: true
metadata: {"TARS":{"emoji":"📅"}}
---

# Daily Tasks

Maintain a high-productivity daily workflow using AI-generated task lists.

## Task List JSON Format

When requested to generate or update the daily task list, always output the following JSON structure exactly:

```json
{
  "date": "YYYY-MM-DD",
  "tasks": [
    {
      "id": "task_001",
      "title": "Task title",
      "description": "Short description",
      "priority": "high",
      "status": "pending"
    }
  ],
  "summary": "Focus area for today."
}
```

### Constraints:
1. **Status**: Must be one of `pending`, `done`, or `skipped`.
2. **Persistence**: The task list is stored in `~/.TARS/workspace/tasks/daily_{YYYY-MM-DD}.json`.
3. **Daily Generation**: A fresh list is generated every morning at 07:00 (default).
4. **Interactive**: In Telegram, each task has buttons: ✅ Done | ⏭ Skip.

## Role of the AI
- **Morning**: When triggered by the CRON job, generate a balanced set of 3-7 tasks based on the user's current context, recent chat history, and any recurring responsibilities.
- **Summary**: Always provide a motivational summary of why these tasks were chosen.
- **On-the-fly Updates**: If the user asks to "add a task", use the `tasks_manager` (via internal logic or prompt) to append to the JSON and refresh the view.

## Handling Commands
- `/tasks`: Show the current list with interactive buttons.
- "Show my tasks" / "What are my tasks today?": Similar to `/tasks`.
- "Add task: [Title]": Add a new item to the list.
