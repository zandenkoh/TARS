"""File Manager skill for TARS."""

from .tools import ListWorkspaceFilesTool, GetFileInfoTool, SendFileToUserTool

def get_tools(workspace, send_callback=None, allowed_dir=None, extra_allowed_dirs=None):
    """Factory to create file_manager tools for AgentLoop."""
    return [
        ListWorkspaceFilesTool(workspace=workspace, allowed_dir=allowed_dir, extra_allowed_dirs=extra_allowed_dirs),
        GetFileInfoTool(workspace=workspace, allowed_dir=allowed_dir, extra_allowed_dirs=extra_allowed_dirs),
        SendFileToUserTool(workspace=workspace, send_callback=send_callback, allowed_dir=allowed_dir, extra_allowed_dirs=extra_allowed_dirs),
    ]
