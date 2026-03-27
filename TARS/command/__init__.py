"""Slash command routing and built-in handlers."""

from TARS.command.builtin import register_builtin_commands
from TARS.command.router import CommandContext, CommandRouter

__all__ = ["CommandContext", "CommandRouter", "register_builtin_commands"]
