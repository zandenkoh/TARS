from TARS.agent.tools.web import _format_results

items = [
    {"title": "<b>Test</b> Title", "url": "https://test.com", "content": "Some snippet"}
]
res = _format_results("test query", items, 1)
print(res)
