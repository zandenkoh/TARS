with open("pyproject.toml", "r") as f:
    content = f.read()

new_content = content.replace('"ddgs>=9.5.5,<10.0.0",', '"duckduckgo-search>=5.0.0,<7.0.0",')

with open("pyproject.toml", "w") as f:
    f.write(new_content)
