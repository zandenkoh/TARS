import asyncio
from unittest.mock import MagicMock, patch

from TARS.agent.tools.web import WebSearchTool


def _fake_resolve_private(*args, **kwargs):
    import socket
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 0))]

async def main():
    tool = WebSearchTool()
    tool.config = MagicMock()
    tool.config.max_results = 5
    tool.config.provider = "searxng"
    tool.config.base_url = "http://169.254.169.254"

    with patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_private):
        res = await tool.execute("test")
        print(f"searxng: {res}")

if __name__ == "__main__":
    asyncio.run(main())
