"""Tools for managing files in the TARS workspace."""

import os
import mimetypes
from pathlib import Path
from typing import Any
from datetime import datetime

from TARS.agent.tools.base import Tool
from TARS.agent.tools.filesystem import _FsTool, _is_under
from TARS.bus.events import OutboundMessage

class SendFileToUserTool(_FsTool):
    """Send a file directly to the user as an upload."""

    def __init__(self, workspace=None, send_callback=None, allowed_dir=None, extra_allowed_dirs=None):
        super().__init__(workspace=workspace, allowed_dir=allowed_dir, extra_allowed_dirs=extra_allowed_dirs)
        self._send_callback = send_callback
        self._default_channel = ""
        self._default_chat_id = ""
        self._default_message_id = None

    def set_context(self, channel: str, chat_id: str, message_id: str | None = None) -> None:
        """Set the current message context."""
        self._default_channel = channel
        self._default_chat_id = chat_id
        self._default_message_id = message_id

    @property
    def name(self) -> str:
        return "send_file_to_user"

    @property
    def description(self) -> str:
        return (
            "Upload a local file directly into the chat. "
            "Use this instead of read_file when you want to send the actual file (e.g. PDF, image, audio) "
            "to the user instead of just showing them the content."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to send (relative to workspace or absolute)"
                },
                "caption": {
                    "type": "string",
                    "description": "Optional message to send along with the file"
                }
            },
            "required": ["path"]
        }

    async def execute(self, path: str, caption: str = "", **kwargs: Any) -> str:
        try:
            if not self._send_callback:
                return "Error: Message sending callback not configured."
            
            fp = self._resolve(path)
            if not fp.exists():
                return f"Error: File not found: {path}"
            
            if not fp.is_file():
                return f"Error: Only files can be sent, not directories: {path}"

            msg = OutboundMessage(
                channel=self._default_channel,
                chat_id=self._default_chat_id,
                content=caption or f"Sent file: {fp.name}",
                media=[str(fp)],
                metadata={"message_id": self._default_message_id}
            )
            
            await self._send_callback(msg)
            return f"Successfully uploaded '{fp.name}' to the chat."
        except Exception as e:
            return f"Error sending file: {e}"

class ListWorkspaceFilesTool(_FsTool):
    """List files in the workspace safely."""

    @property
    def name(self) -> str:
        return "list_workspace_files"

    @property
    def description(self) -> str:
        return "List files and directories within the TARS workspace (~/.TARS/workspace/)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path within the workspace (default '.')",
                    "default": "."
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list subdirectories recursively",
                    "default": False
                }
            }
        }

    async def execute(self, path: str = ".", recursive: bool = False, **kwargs: Any) -> str:
        try:
            # Always ensure we are within the workspace
            root = self._workspace
            if not root:
                return "Error: Workspace path not configured."
            
            target = (root / path).resolve()
            if not _is_under(target, root):
                return f"Error: Path '{path}' is outside the workspace."
            
            if not target.exists():
                return f"Error: Path '{path}' does not exist."
            
            if not target.is_dir():
                return f"Error: Path '{path}' is not a directory."

            items = []
            pattern = "**/*" if recursive else "*"
            
            for p in sorted(target.glob(pattern)):
                # Ignore common noise
                if any(part.startswith(".") or part == "__pycache__" for part in p.parts):
                    continue
                
                rel = p.relative_to(root)
                is_dir = p.is_dir()
                size = p.stat().st_size if not is_dir else 0
                icon = "📁" if is_dir else "📄"
                
                size_str = f" ({size} bytes)" if not is_dir else ""
                items.append(f"{icon} {rel}{size_str}")

            if not items:
                return f"Workspace directory '{path}' is empty."

            return "\n".join(items)
        except Exception as e:
            return f"Error listing workspace files: {e}"

class GetFileInfoTool(_FsTool):
    """Get detailed information about a file."""

    @property
    def name(self) -> str:
        return "get_file_info"

    @property
    def description(self) -> str:
        return "Get detailed metadata about a file in the workspace (size, type, dates)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (relative to workspace or absolute)"
                }
            },
            "required": ["path"]
        }

    async def execute(self, path: str, **kwargs: Any) -> str:
        try:
            fp = self._resolve(path)
            if not fp.exists():
                return f"Error: File not found: {path}"
            
            stat = fp.stat()
            is_dir = fp.is_dir()
            mime, _ = mimetypes.guess_type(str(fp))
            
            info = [
                f"Path: {fp}",
                f"Type: {'Directory' if is_dir else 'File'}",
                f"MIME Type: {mime or 'unknown'}",
                f"Size: {stat.st_size} bytes",
                f"Created: {datetime.fromtimestamp(stat.st_ctime).isoformat()}",
                f"Modified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}",
            ]
            
            # Add a small preview for text files
            if not is_dir and stat.st_size > 0 and (mime and (mime.startswith("text/") or mime == "application/json")):
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        preview = f.read(500)
                        info.append(f"\nPreview:\n---\n{preview}{'...' if stat.st_size > 500 else ''}\n---")
                except Exception:
                    pass
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting file info: {e}"
