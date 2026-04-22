import os

with open("TARS/channels/qq.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Add validate_url_target back to _read_media_bytes if not already there
old_code_1 = """        if not self._http:
            self._http = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120))
        try:
            from urllib.parse import urljoin"""

new_code_1 = """        ok, err = validate_url_target(media_ref)
        if not ok:
            logger.warning("QQ outbound media URL validation failed url={} err={}", media_ref, err)
            return None, None

        if not self._http:
            self._http = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120))
        try:
            from urllib.parse import urljoin"""

if old_code_1 in content:
    content = content.replace(old_code_1, new_code_1)

# Fix 2: the indentation for the rest of _download_to_media_dir_chunked
old_code_2 = """                    # Infer extension: url -> filename_hint -> content-type -> fallback
                    ext = Path(urlparse(current_url).path).suffix
                if not ext:
                    ext = Path(filename_hint).suffix
                if not ext:
                    if "png" in ctype:
                        ext = ".png"
                    elif "jpeg" in ctype or "jpg" in ctype:
                        ext = ".jpg"
                    elif "gif" in ctype:
                        ext = ".gif"
                    elif "webp" in ctype:
                        ext = ".webp"
                    elif "pdf" in ctype:
                        ext = ".pdf"
                    else:
                        ext = ".bin"

                if safe:
                    if not Path(safe).suffix:
                        safe = safe + ext
                    filename = safe
                else:
                    filename = f"qq_file_{ts}{ext}"

                target = self._media_root / filename
                if target.exists():
                    target = self._media_root / f"{target.stem}_{ts}{target.suffix}"

                tmp_path = target.with_suffix(target.suffix + ".part")

                # Stream write
                downloaded = 0
                chunk_size = max(1024, int(self.config.download_chunk_size or 262144))
                max_bytes = max(
                    1024 * 1024, int(self.config.download_max_bytes or (200 * 1024 * 1024))
                )

                def _open_tmp():
                    tmp_path.parent.mkdir(parents=True, exist_ok=True)
                    return open(tmp_path, "wb")  # noqa: SIM115

                f = await asyncio.to_thread(_open_tmp)
                try:
                    async for chunk in resp.content.iter_chunked(chunk_size):
                        if not chunk:
                            continue
                        downloaded += len(chunk)
                        if downloaded > max_bytes:
                            logger.warning(
                                "QQ download exceeded max_bytes={} url={} -> abort",
                                max_bytes,
                                url,
                            )
                            return None
                        await asyncio.to_thread(f.write, chunk)
                finally:
                    await asyncio.to_thread(f.close)

                # Atomic rename
                await asyncio.to_thread(os.replace, tmp_path, target)
                tmp_path = None  # mark as moved
                logger.info("QQ file saved: {}", str(target))
                return str(target)"""

new_code_2 = """                    # Infer extension: url -> filename_hint -> content-type -> fallback
                    ext = Path(urlparse(current_url).path).suffix
                    if not ext:
                        ext = Path(filename_hint).suffix
                    if not ext:
                        if "png" in ctype:
                            ext = ".png"
                        elif "jpeg" in ctype or "jpg" in ctype:
                            ext = ".jpg"
                        elif "gif" in ctype:
                            ext = ".gif"
                        elif "webp" in ctype:
                            ext = ".webp"
                        elif "pdf" in ctype:
                            ext = ".pdf"
                        else:
                            ext = ".bin"

                    if safe:
                        if not Path(safe).suffix:
                            safe = safe + ext
                        filename = safe
                    else:
                        filename = f"qq_file_{ts}{ext}"

                    target = self._media_root / filename
                    if target.exists():
                        target = self._media_root / f"{target.stem}_{ts}{target.suffix}"

                    tmp_path = target.with_suffix(target.suffix + ".part")

                    # Stream write
                    downloaded = 0
                    chunk_size = max(1024, int(self.config.download_chunk_size or 262144))
                    max_bytes = max(
                        1024 * 1024, int(self.config.download_max_bytes or (200 * 1024 * 1024))
                    )

                    def _open_tmp():
                        tmp_path.parent.mkdir(parents=True, exist_ok=True)
                        return open(tmp_path, "wb")  # noqa: SIM115

                    f = await asyncio.to_thread(_open_tmp)
                    try:
                        async for chunk in resp.content.iter_chunked(chunk_size):
                            if not chunk:
                                continue
                            downloaded += len(chunk)
                            if downloaded > max_bytes:
                                logger.warning(
                                    "QQ download exceeded max_bytes={} url={} -> abort",
                                    max_bytes,
                                    url,
                                )
                                return None
                            await asyncio.to_thread(f.write, chunk)
                    finally:
                        await asyncio.to_thread(f.close)

                    # Atomic rename
                    await asyncio.to_thread(os.replace, tmp_path, target)
                    tmp_path = None  # mark as moved
                    logger.info("QQ file saved: {}", str(target))
                    return str(target)"""

if old_code_2 in content:
    content = content.replace(old_code_2, new_code_2)

with open("TARS/channels/qq.py", "w", encoding="utf-8") as f:
    f.write(content)
