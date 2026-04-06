import re

with open('TARS/channels/qq.py', 'r') as f:
    content = f.read()

safe_get_code_old = """@asynccontextmanager
async def _safe_aiohttp_get(session: aiohttp.ClientSession, url: str, **kwargs):
    max_redirects = 5
    current_url = url
    kwargs.pop("allow_redirects", None)
    for _ in range(max_redirects):
        resp = await session.get(current_url, allow_redirects=False, **kwargs)
        if resp.status in (301, 302, 303, 307, 308) and "Location" in resp.headers:
            current_url = resp.headers["Location"]
            resp.close()
            ok, err = validate_resolved_url(current_url)
            if not ok:
                raise RuntimeError(f"SSRF blocked on redirect: {err}")
            continue
        try:
            yield resp
        finally:
            resp.close()
        return
    raise RuntimeError("Too many redirects")"""

safe_get_code_new = """from urllib.parse import urljoin
@asynccontextmanager
async def _safe_aiohttp_get(session: aiohttp.ClientSession, url: str, **kwargs):
    max_redirects = 5
    current_url = url
    kwargs.pop("allow_redirects", None)
    for _ in range(max_redirects):
        resp = await session.get(current_url, allow_redirects=False, **kwargs)
        if resp.status in (301, 302, 303, 307, 308) and "Location" in resp.headers:
            location = resp.headers["Location"]
            current_url = urljoin(current_url, location)
            resp.close()
            ok, err = validate_resolved_url(current_url)
            if not ok:
                raise RuntimeError(f"SSRF blocked on redirect: {err}")
            continue
        try:
            yield resp
        finally:
            resp.close()
        return
    raise RuntimeError("Too many redirects")"""

content = content.replace(safe_get_code_old, safe_get_code_new)

with open('TARS/channels/qq.py', 'w') as f:
    f.write(content)
