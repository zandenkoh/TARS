---
name: file_manager
description: Manage and discover files in the TARS workspace.
always: true
metadata: {"TARS":{"emoji":"📁"}}
---

# File Manager

Use these tools to discover, analyze, and send files from your local workspace (`~/.TARS/workspace/`).

## Capabilities

1. **List Files**: View the contents of your workspace or specific subdirectories.
2. **File Info**: Get details about a file (size, type, last modified).
3. **Search**: Find files by name.
4. **Sending Files**: To send a file to the user, use the `message` tool and include the absolute path to the file in the `media` list.

## Usage Examples

### Sending a report
If the user asks for a file (like a PDF or image), do NOT use `read_file` to print it in the chat. Instead, use the `send_file_to_user` tool:
1. Call `send_file_to_user(path="reports/report_2024.pdf", caption="Here is the report you requested.")`

### Analyzing an upload
When a user uploads a file, it will appear in your context as `[file_uploaded: /path/to/file]`. 
1. Call `get_file_info(path="/path/to/file")` to check its size and type.
2. Call `read_file(path="/path/to/file")` ONLY if you need to analyze the text content yourself.
3. If the user wants you to "send it back" or "forward it", use `send_file_to_user`.

## Workspace Structure
- **uploads/**: User-uploaded files from Telegram or WebUI are saved here, usually in `YYYY-MM-DD` subdirectories.
- **media/**: General media storage.
- **tasks/**: Daily task JSON files.
