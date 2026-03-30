"""Tests for exec tool internal URL blocking."""

from __future__ import annotations

import socket
from unittest.mock import patch

import pytest

from TARS.agent.tools.shell import ExecTool


def _fake_resolve_private(hostname, port, family=0, type_=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 0))]


def _fake_resolve_localhost(hostname, port, family=0, type_=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0))]


def _fake_resolve_public(hostname, port, family=0, type_=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))]


@pytest.mark.asyncio
async def test_exec_blocks_curl_metadata():
    tool = ExecTool()
    with patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_private):
        result = await tool.execute(
            command='curl -s -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/'
        )
    assert "Error" in result
    assert "internal" in result.lower() or "private" in result.lower()


@pytest.mark.asyncio
async def test_exec_blocks_wget_localhost():
    tool = ExecTool()
    with patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_localhost):
        result = await tool.execute(command="wget http://localhost:8080/secret -O /tmp/out")
    assert "Error" in result


@pytest.mark.asyncio
async def test_exec_allows_normal_commands():
    tool = ExecTool(timeout=5)
    result = await tool.execute(command="echo hello")
    assert "hello" in result
    assert "Error" not in result.split("\n")[0]


@pytest.mark.asyncio
async def test_exec_allows_curl_to_public_url():
    """Commands with public URLs should not be blocked by the internal URL check."""
    tool = ExecTool()
    with patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_public):
        guard_result = tool._guard_command("curl https://example.com/api", "/tmp")
    assert guard_result is None


@pytest.mark.asyncio
async def test_exec_blocks_chained_internal_url():
    """Internal URLs buried in chained commands should still be caught."""
    tool = ExecTool()
    with patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_private):
        result = await tool.execute(
            command="echo start && curl http://169.254.169.254/latest/meta-data/ && echo done"
        )
    assert "Error" in result


@pytest.mark.asyncio
async def test_exec_restrict_to_workspace_blocks_outside_working_dir(tmp_path):
    """Test that a working_dir outside the workspace is blocked when restrict_to_workspace=True."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    tool = ExecTool(
        working_dir=str(workspace),
        workspace_dir=workspace,
        restrict_to_workspace=True,
    )

    # Try to execute a command with a working_dir outside the workspace
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    result = await tool.execute(command="ls", working_dir=str(outside_dir))
    assert "Error" in result
    assert "working directory outside workspace" in result.lower()


@pytest.mark.asyncio
async def test_exec_restrict_to_workspace_blocks_outside_absolute_paths(tmp_path):
    """Test that an absolute path outside the workspace is blocked when restrict_to_workspace=True."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    tool = ExecTool(
        working_dir=str(workspace),
        workspace_dir=workspace,
        restrict_to_workspace=True,
    )

    # Try to execute a command with an absolute path outside the workspace
    outside_file = tmp_path / "outside.txt"
    result = await tool.execute(command=f"cat {outside_file}")
    assert "Error" in result
    assert "path outside workspace" in result.lower()

    # Absolute path inside the workspace should be allowed
    inside_file = workspace / "inside.txt"
    inside_file.touch()

    # We just want to check that it doesn't return the safety guard error
    guard_error = tool._guard_command(f"cat {inside_file}", str(workspace))
    assert guard_error is None


@pytest.mark.asyncio
async def test_exec_restrict_to_workspace_blocks_path_traversal(tmp_path):
    """Test that path traversal (../) is blocked when restrict_to_workspace=True."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    tool = ExecTool(
        working_dir=str(workspace),
        workspace_dir=workspace,
        restrict_to_workspace=True,
    )

    result = await tool.execute(command="cat ../outside.txt")
    assert "Error" in result
    assert "path traversal detected" in result.lower()
