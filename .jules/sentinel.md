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
## 2026-04-01 - Prevent SSRF via HTTP Redirects in WebFetchTool

**Vulnerability:** The `WebFetchTool` used `httpx.AsyncClient` with `follow_redirects=True` and only validated the final resolved URL after the request had been fully processed. This allowed Server-Side Request Forgery (SSRF) where an attacker-controlled external URL could redirect the agent to fetch internal, private IP addresses (e.g., `127.0.0.1` or AWS metadata endpoints).
**Learning:** Validating a URL *after* a request has been made provides no security against SSRF when redirects are followed automatically by the HTTP client. The request to the private IP has already occurred.
**Prevention:** When following HTTP redirects, use event hooks (e.g., `event_hooks={"request": [...]}` in `httpx`) to validate each URL in the redirect chain *before* the request is actually sent.
## 2025-03-31 - [ExecTool Directory Traversal Bypass]

**Vulnerability:** The `ExecTool` safety guard `_guard_command` relies on simple substring matching (`"../"` or `".."`) to enforce `restrict_to_workspace`. This check is easily bypassed by subshell commands using `cd ..`, allowing execution outside the restricted workspace (e.g. `cd .. && cat /etc/passwd`).

**Learning:** In a lightweight agent architecture utilizing raw shell command execution without heavy containerization per-tool, simplistic string checks for directory traversal fail against shell syntax variations. The shell evaluates bounded occurrences of `..` as parent directories even if they don't explicitly contain slashes.

**Prevention:** Use a comprehensive regex boundary check like `r'(?:^|[\s"\'|<>&;/\\=])\.\.(?:[\s"\'|<>&;/\\=]|$)'` to detect `..` used as a standalone path component, intercepting subshell navigations while allowing legitimate filenames like `foo..bar`.
## 2026-03-22 - Prevent SSRF via HTTP Redirects in MCP Client Setup

**Vulnerability:** The TARS `mcp.py` client utilized `httpx.AsyncClient` with `follow_redirects=True` for connecting to MCP servers via `sse` and `streamableHttp` transports. However, there was no validation of the target URL before attempting the connection, and no validation of URLs during HTTP redirects. This allowed Server-Side Request Forgery (SSRF) where a malicious server configuration could target or redirect to internal, private IP addresses.
**Learning:** Like `WebFetchTool`, the MCP client's HTTP transports must validate both the initial connection URL and any subsequent redirects to prevent internal network scanning or interaction.
**Prevention:** Always validate user-provided URLs using `validate_url_target` before establishing connections, and use event hooks (e.g., `event_hooks={"request": [_verify_request]}`) to validate each URL in the redirect chain before the request is actually sent.

## 2026-04-01 - Prevent SSRF in SearXNG Web Search Provider

**Vulnerability:** The `WebSearchTool` in `TARS/agent/tools/web.py` allowed users to specify a custom `SEARXNG_BASE_URL`. The tool only validated the URL scheme and domain using `_validate_url` before making an HTTP GET request to this endpoint. This allowed Server-Side Request Forgery (SSRF) because an attacker could configure a URL that resolves to an internal/private IP address (e.g., `169.254.169.254` or `127.0.0.1`), bypassing the basic URL validation.
**Learning:** Basic URL scheme and domain validation is insufficient when dealing with user-configured endpoints. The underlying IP address must be resolved and checked against a list of private/internal networks to prevent SSRF.
**Prevention:** Always use `validate_url_target` (or wrappers like `_validate_url_safe`) which resolve hostnames and explicitly block private/internal IP addresses before sending HTTP requests to user-controlled endpoints.

## 2026-04-01 - [Harden WebUI CORS and Security Headers]

**Vulnerability:** The local WebUI (`TARS/webui/api.py`) used `allow_origins=["*"]` along with `allow_credentials=True` in its CORS middleware.
**Learning:** In a locally hosted web app that allows cross-origin requests globally, any public website visited by the user can make authenticated requests to the local port (e.g., extracting API keys from the configuration endpoint). While Starlette attempts to block `allow_origins=["*"]` with credentials, it dynamically reflects the `Origin` header, creating a severe data exposure vulnerability.
**Prevention:** Strictly enforce `allow_origins` to known safe local endpoints (e.g., `http://localhost:18790`) and inject secure headers (`X-Frame-Options`, `X-Content-Type-Options`) via custom middleware for all sensitive local-bound UI routes.
