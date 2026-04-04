
## 2026-04-04 - Prevent Command Injection Bypass in ExecTool

**Vulnerability:** The `ExecTool` used `asyncio.create_subprocess_shell` (`shell=True`) to execute shell commands. This delegates command parsing to the system shell, which makes regex-based blocklists vulnerable to command injection bypass via shell operators (like pipes and redirection).
**Learning:** In a lightweight agent architecture with shell capabilities, relying on regex blocklists combined with `shell=True` is insufficient because the shell can interpret operators that regex might miss or be bypassed by.
**Prevention:** Parse commands securely using `shlex.split()` (wrapped in a `try...except ValueError` block to handle malformed input) and execute them with `asyncio.create_subprocess_exec` (`shell=False`). This intentionally disables standard shell features to guarantee execution safety.
