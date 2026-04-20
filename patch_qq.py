with open("TARS/channels/qq.py", "r") as f:
    content = f.read()

# Let's fix the bugs:
# 1. Missing validate_url_target import
# 2. Missing validation on the initial URL before the loop
# 3. Import urljoin at the top or outside the loop

search_block1 = """
        try:
            from TARS.security.network import validate_resolved_url
            redirects = 0
            current_url = media_ref
            while redirects < 5:
                async with self._http.get(current_url, allow_redirects=False) as resp:
"""

replace_block1 = """
        try:
            from TARS.security.network import validate_resolved_url, validate_url_target
            from urllib.parse import urljoin

            ok, err = validate_url_target(media_ref)
            if not ok:
                logger.warning("QQ outbound media URL SSRF blocked url={} err={}", media_ref, err)
                return None, None
            ok, err = validate_resolved_url(media_ref)
            if not ok:
                logger.warning("QQ outbound media URL SSRF blocked url={} err={}", media_ref, err)
                return None, None

            redirects = 0
            current_url = media_ref
            while redirects < 5:
                async with self._http.get(current_url, allow_redirects=False) as resp:
"""
content = content.replace(search_block1.strip('\n'), replace_block1.strip('\n'))

search_block2 = """
        try:
            from TARS.security.network import validate_resolved_url
            redirects = 0
            current_url = url
            while redirects < 5:
                async with self._http.get(
                    current_url,
                    timeout=aiohttp.ClientTimeout(total=120),
                    allow_redirects=False,
                ) as resp:
"""

replace_block2 = """
        try:
            from TARS.security.network import validate_resolved_url, validate_url_target
            from urllib.parse import urljoin

            ok, err = validate_url_target(url)
            if not ok:
                logger.warning("QQ inbound media SSRF blocked url={} err={}", url, err)
                return None
            ok, err = validate_resolved_url(url)
            if not ok:
                logger.warning("QQ inbound media SSRF blocked url={} err={}", url, err)
                return None

            redirects = 0
            current_url = url
            while redirects < 5:
                async with self._http.get(
                    current_url,
                    timeout=aiohttp.ClientTimeout(total=120),
                    allow_redirects=False,
                ) as resp:
"""
content = content.replace(search_block2.strip('\n'), replace_block2.strip('\n'))

search_block3 = """
                        if not location:
                            return None, None
                        from urllib.parse import urljoin
                        current_url = urljoin(current_url, location)
"""

replace_block3 = """
                        if not location:
                            return None, None
                        current_url = urljoin(current_url, location)
"""
content = content.replace(search_block3.strip('\n'), replace_block3.strip('\n'))

search_block4 = """
                        if not location:
                            return None
                        from urllib.parse import urljoin
                        current_url = urljoin(current_url, location)
"""

replace_block4 = """
                        if not location:
                            return None
                        current_url = urljoin(current_url, location)
"""
content = content.replace(search_block4.strip('\n'), replace_block4.strip('\n'))

with open("TARS/channels/qq.py", "w") as f:
    f.write(content)

print("Replacement successful" if search_block1.strip('\n') not in content and search_block2.strip('\n') not in content and search_block3.strip('\n') not in content and search_block4.strip('\n') not in content else "Replacement failed")
