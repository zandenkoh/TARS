import os

journal_path = '.jules/sentinel.md'
os.makedirs(os.path.dirname(journal_path), exist_ok=True)

entry = """
## 2026-04-01 - SSRF in QQ Channel via aiohttp redirects

**Vulnerability:** The QQ channel was using `aiohttp` to download media with `allow_redirects=True`. While the initial URL was validated against SSRF (`validate_url_target`), `aiohttp` would blindly follow redirects, allowing an attacker-controlled external server to redirect the request to internal TARS services (like `http://localhost:18790`) or cloud metadata endpoints (`169.254.169.254`).
**Learning:** `aiohttp` follows redirects by default (`allow_redirects=True`), unlike `httpx`. When implementing custom redirect loops with `allow_redirects=False` to prevent SSRF, one must handle relative `Location` headers using `urllib.parse.urljoin`, otherwise `aiohttp` will crash with `ValueError: URL should be absolute`.
**Prevention:** Replace `allow_redirects=True` with a custom `@asynccontextmanager` redirect loop that reads the `Location` header, resolves it safely with `urljoin`, and applies `validate_resolved_url` on the target before following the redirect.
"""

if not os.path.exists(journal_path):
    with open(journal_path, 'w') as f:
        f.write("# Sentinel Journal\n" + entry)
else:
    with open(journal_path, 'a') as f:
        f.write(entry)
