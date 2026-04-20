import asyncio
from TARS.channels.qq import QQChannel

class MockConfig:
    download_chunk_size = 262144
    download_max_bytes = 200 * 1024 * 1024
