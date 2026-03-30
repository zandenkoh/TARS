import re

with open("TARS/agent/tools/web.py", "r") as f:
    content = f.read()

# I am not going to touch web.py. I'm going to update tests/tools/test_web_search_tool.py
# Wait, if the issue description is:
# "Current Code:
# def _format_results(query: str, items: list[dict[str, Any]], n: int) -> str:
#     if not items:
#         return f"No results found for '{query}'."
#     res = [f"Search results for '{query}':\n"]"
#
# But in TARS/agent/tools/web.py it actually is:
# def _format_results(query: str, items: list[dict[str, Any]], n: int) -> str:
#     if not items:
#         return f"No results for: {query}"
#     lines = [f"Results for: {query}\n"]
