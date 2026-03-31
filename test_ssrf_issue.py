import asyncio
from unittest.mock import MagicMock

from TARS.agent.tools.web import WebFetchTool


async def main():
    tool = WebFetchTool()
    tool.config = MagicMock()
    # Test if Jina fetching is protected
    try:
        await tool._fetch_jina("http://example.com", 100)
        print("Success")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
