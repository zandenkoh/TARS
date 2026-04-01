## 2026-04-01 - Prevent Sandbox Escape in File Tools

**Vulnerability:** The `_resolve_path` function in `TARS/agent/tools/filesystem.py` allowed path traversal and absolute path injection to escape the intended `workspace` directory. Because the code only conditionally verified the bounds when `allowed_dir` was set, providing an absolute path like `/etc/passwd` to file tools (e.g. `read_file`, `write_file`) would silently bypass the workspace restriction.
**Learning:** In a minimal agent architecture, bounding boxes like `workspace` must be enforced consistently at the point of path resolution, irrespective of optional constraints like `allowed_dir`.
**Prevention:** Ensured `_is_under(resolved, workspace)` is explicitly checked for every path resolution if a `workspace` is configured, guaranteeing that tools cannot operate outside this boundary.

## 2026-04-01 - Prevent Sandbox Escape in ExecTool via Command Path Extraction

**Vulnerability:** In `TARS/agent/tools/shell.py`, the path extraction regular expressions `_WIN_PATH_RE`, `_POSIX_PATH_RE`, and `_HOME_PATH_RE` used by `_extract_absolute_paths` failed to identify absolute paths that immediately follow an assignment operator `=` or backtick `` ` `` without spaces. This allowed an attacker to bypass the `restrict_to_workspace` sandbox by crafting shell commands like `cat --file=/etc/passwd` or `cat \`/etc/passwd\``.
**Learning:** When attempting to extract and restrict paths within raw shell commands, security mechanisms must account for all valid shell contexts where a path might begin. Simple whitespace or command separator boundaries are insufficient because arguments are frequently passed via assignment (`=`) or command substitution (`` ` ``).
**Prevention:** Expanded the boundary character classes in the path extraction regexes (e.g., changing `[\s|<>&;\(\)'\"]` to `[\s|<>&;\(\)'\"=\`]`) to ensure absolute paths are reliably identified and validated regardless of the preceding shell punctuation.
