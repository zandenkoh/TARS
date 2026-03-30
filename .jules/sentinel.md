## YYYY-MM-DD - Path Traversal in WebUI Uploads and Moves

**Vulnerability:** The `/api/workspace/upload` and `/api/workspace/move` endpoints in the TARS web UI dashboard did not adequately validate that the resulting file path, after combining `target_dir` with the attacker-controlled `file.filename` or `src_path.name`, remained within the bounds of the workspace directory. This could lead to an arbitrary file write out of the workspace sandbox.
**Learning:** Even if the initial target directory is resolved and validated, appending an unsanitized filename or source name can re-introduce path traversal (e.g., `../../../`) prior to file writing.
**Prevention:** Always `resolve()` the final combined file path and enforce `str(file_path).startswith(str(base.resolve()))` immediately before opening or writing to the file, especially when dealing with user-uploaded file names or destination paths in file operations.
## 2024-05-24 - Path Traversal in File Writing Endpoints
**Vulnerability:** Found a critical path traversal vulnerability in `TARS/webui/api.py` `create_task` endpoint. User input (the `date` field) was directly concatenated into the filename without resolving the final path against the workspace boundary.
**Learning:** Even internal tool endpoints must validate the final resolved file paths against the base directory boundaries. The `.resolve().is_relative_to()` combination is the correct standard for this validation.
**Prevention:** Always validate constructed paths before file I/O using `.resolve()` and `.is_relative_to()` to guarantee that inputs don't escape their designated directories.
## 2024-05-24 - XSS via Manual HTML Construction in SSE Stream
**Vulnerability:** A Cross-Site Scripting (XSS) vulnerability was found in the `chat_stream` SSE endpoint in `TARS/webui/api.py`. The LLM text output (`delta`) and the executed tool name (`text`) were directly concatenated into HTML strings and served via HTMX without HTML escaping, allowing potential malicious LLM responses or tool outputs to inject arbitrary scripts.
**Learning:** Even when output is expected to be plain text or Markdown, if the backend constructs HTML fragments manually (e.g., for SSE streams with HTMX swaps) instead of using a templating engine like Jinja2 which auto-escapes by default, it introduces a severe risk of XSS if the data isn't explicitly sanitized.
**Prevention:** Always use `html.escape()` when manually constructing HTML strings from external or untrusted data sources (including LLM responses and dynamic tool execution outputs) before serving them to the client.
## 2025-03-05 - 🛡️ Sentinel: [CRITICAL] Prevent Sandbox Escape in ExecTool via Manipulated working_dir

**Vulnerability:** In `TARS/agent/tools/shell.py`, the `restrict_to_workspace` security guard verified that absolute paths in the command fell within the `cwd` (`working_dir`). However, an LLM could supply an arbitrary `working_dir` (e.g., `/etc`) when calling the tool, silently shifting the bounding box and completely bypassing the workspace sandbox to execute arbitrary system commands and access files. Additionally, the path boundary check used a flawed `not in p.parents` logic instead of strict relative path checks.

**Learning:** In a lightweight agent architecture where tools dynamically accept arguments like `working_dir` from an untrusted source (the LLM), security boundaries *must* be rooted in statically initialized configuration (like a definitive `workspace_dir`) and must never fail-open.

**Prevention:**
1. Always securely initialize bounding directories (`workspace_dir`) directly from the system configuration (`agent/loop.py`) instead of relying on tool execution arguments.
2. Use strict `Path.is_relative_to()` to validate all resolved paths (both `cwd` and command targets) against the definitive `workspace_dir`.
3. Ensure security checks do not fail-open: if `restrict_to_workspace` is active but `workspace_dir` is undefined, the guard must explicitly block execution.
