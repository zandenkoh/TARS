import re

with open("TARS/channels/qq.py", "r", encoding="utf-8") as f:
    content = f.read()

search1 = """        try:
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
            return None, None"""

replace1 = """        try:
            from urllib.parse import urljoin
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
                    current_url = urljoin(current_url, location)
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
            return None, None"""

content = content.replace(search1, replace1)

search2 = """        try:
            current_url = url
            redirects = 0
            resp = None
            while redirects < 5:
                resp = await self._http.get(
                    current_url,
                    timeout=aiohttp.ClientTimeout(total=120),
                    allow_redirects=False,
                )
                if resp.status in (301, 302, 303, 307, 308):
                    redirects += 1
                    location = resp.headers.get("Location")
                    if not location:
                        resp.release()
                        return None
                    current_url = location
                    ok, err = validate_resolved_url(current_url)
                    if not ok:
                        logger.warning("QQ download SSRF redirect blocked url={} err={}", current_url, err)
                        resp.release()
                        return None
                    resp.release()
                    continue
                break

            if redirects >= 5 or not resp:
                if resp: resp.release()
                logger.warning("QQ download exceeded max redirects url={}", url)
                return None"""

replace2 = """        try:
            from urllib.parse import urljoin
            # Initial validation
            ok, err = validate_url_target(url)
            if not ok:
                logger.warning("QQ download SSRF blocked url={} err={}", url, err)
                return None

            current_url = url
            redirects = 0
            resp = None
            while redirects < 5:
                resp = await self._http.get(
                    current_url,
                    timeout=aiohttp.ClientTimeout(total=120),
                    allow_redirects=False,
                )
                if resp.status in (301, 302, 303, 307, 308):
                    redirects += 1
                    location = resp.headers.get("Location")
                    if not location:
                        resp.release()
                        return None
                    current_url = urljoin(current_url, location)
                    ok, err = validate_resolved_url(current_url)
                    if not ok:
                        logger.warning("QQ download SSRF redirect blocked url={} err={}", current_url, err)
                        resp.release()
                        return None
                    resp.release()
                    continue
                break

            if redirects >= 5 or not resp:
                if resp: resp.release()
                logger.warning("QQ download exceeded max redirects url={}", url)
                return None"""

content = content.replace(search2, replace2)

with open("TARS/channels/qq.py", "w", encoding="utf-8") as f:
    f.write(content)
