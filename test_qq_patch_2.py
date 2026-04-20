import re

with open("TARS/channels/qq.py", "r", encoding="utf-8") as f:
    content = f.read()

diff1 = """<<<<<<< SEARCH
        try:
            current_url = media_ref
            redirects = 0
            while redirects < 5:
                resp = await self._http.get(current_url, allow_redirects=False)
                if resp.status in (301, 302, 303, 307, 308):
                    redirects += 1
                    location = resp.headers.get("Location")
                    if not location:
                        resp.release()
                        return None, None
                    current_url = location
                    ok, err = validate_resolved_url(current_url)
                    if not ok:
                        logger.warning("QQ outbound media SSRF redirect blocked url={} err={}", current_url, err)
                        resp.release()
                        return None, None
                    resp.release()
                    continue

                if resp.status >= 400:
                    logger.warning(
                        "QQ outbound media download failed status={} url={}",
                        resp.status,
                        current_url,
                    )
                    resp.release()
                    return None, None
                data = await resp.read()
                resp.release()
                if not data:
                    return None, None
                filename = os.path.basename(urlparse(current_url).path) or "file.bin"
                return data, filename
            logger.warning("QQ outbound media download exceeded max redirects url={}", media_ref)
            return None, None
        except Exception as e:
            logger.warning("QQ outbound media download error url={} err={}", media_ref, e)
            return None, None
=======
        try:
            current_url = media_ref
            redirects = 0
            while redirects < 5:
                resp = await self._http.get(current_url, allow_redirects=False)
                if resp.status in (301, 302, 303, 307, 308):
                    redirects += 1
                    location = resp.headers.get("Location")
                    if not location:
                        resp.release()
                        return None, None
                    current_url = str(resp.url.join(aiohttp.helpers.URL(location))) if hasattr(aiohttp, "helpers") else str(resp.url.join(resp.url.build(path=location)))

                    # For aiohttp, the safer way is to use yarl.URL if possible, or urljoin.
                    # Let's import urljoin.
>>>>>>> REPLACE"""

import difflib

def apply_diff(content, diff):
    search_block = diff.split("<<<<<<< SEARCH\n")[1].split("\n=======\n")[0]
    if search_block not in content:
        print("Search block not found")
        return
    print("Search block found")

apply_diff(content, diff1)
