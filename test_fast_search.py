
lines = []
for i in range(1000):
    lines.append('{"role": "user", "content": "Just a normal message without the keyword."}')
lines.append('{"role": "assistant", "content": "I am the AI assistant."}')

def with_lower(query_lower, text):
    return query_lower in text.lower()

def without_lower(query_lower, text):
    # This might have false negatives for case-insensitive search if we don't lower the line, but wait:
    # If the text is JSON, we still need case-insensitive match for the keyword.
    # But `.lower()` on a 1MB string might be slow.
    pass
