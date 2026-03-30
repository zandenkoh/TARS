## YYYY-MM-DD - Path Traversal in WebUI Uploads and Moves

**Vulnerability:** The `/api/workspace/upload` and `/api/workspace/move` endpoints in the TARS web UI dashboard did not adequately validate that the resulting file path, after combining `target_dir` with the attacker-controlled `file.filename` or `src_path.name`, remained within the bounds of the workspace directory. This could lead to an arbitrary file write out of the workspace sandbox.
**Learning:** Even if the initial target directory is resolved and validated, appending an unsanitized filename or source name can re-introduce path traversal (e.g., `../../../`) prior to file writing.
**Prevention:** Always `resolve()` the final combined file path and enforce `str(file_path).startswith(str(base.resolve()))` immediately before opening or writing to the file, especially when dealing with user-uploaded file names or destination paths in file operations.
