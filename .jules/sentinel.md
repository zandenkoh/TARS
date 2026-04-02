## 2026-04-01 - Prevent SSRF Vulnerability in DingTalk File Downloads

**Vulnerability:** The `_download_file_if_present` method in `TARS/channels/dingtalk.py` requests a temporary download URL from DingTalk, then fetches it blindly. A malicious external API or manipulated URL could direct the agent to fetch internal network resources or cloud metadata (SSRF).
**Learning:** External API responses containing URLs must be treated as untrusted input. In an agent architecture, SSRF protections like `validate_url_target` must be applied to dynamically received URLs before passing them to HTTP clients, even when using seemingly "trusted" third-party APIs.
**Prevention:** Ensured `validate_url_target` is invoked on the dynamically resolved `downloadUrl` before attempting the download via `httpx`.

## 2026-04-01 - Prevent Sandbox Escape in File Tools

**Vulnerability:** The `_resolve_path` function in `TARS/agent/tools/filesystem.py` allowed path traversal and absolute path injection to escape the intended `workspace` directory. Because the code only conditionally verified the bounds when `allowed_dir` was set, providing an absolute path like `/etc/passwd` to file tools (e.g. `read_file`, `write_file`) would silently bypass the workspace restriction.
**Learning:** In a minimal agent architecture, bounding boxes like `workspace` must be enforced consistently at the point of path resolution, irrespective of optional constraints like `allowed_dir`.
**Prevention:** Ensured `_is_under(resolved, workspace)` is explicitly checked for every path resolution if a `workspace` is configured, guaranteeing that tools cannot operate outside this boundary.