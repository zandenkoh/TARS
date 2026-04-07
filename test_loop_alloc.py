import timeit
from datetime import datetime

class DummySession:
    def __init__(self):
        self.messages = []

def original():
    session = DummySession()
    messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"}
    ] * 100
    skip = 0
    from datetime import datetime
    for m in messages[skip:]:
        entry = dict(m)
        role, content = entry.get("role"), entry.get("content")
        if role == "assistant" and not content and not entry.get("tool_calls"):
            continue
        entry.setdefault("timestamp", datetime.now().isoformat())
        session.messages.append(entry)

def optimized():
    session = DummySession()
    messages = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"}
    ] * 100
    skip = 0
    from datetime import datetime

    append = session.messages.append
    get_now = datetime.now

    for m in messages[skip:]:
        role = m.get("role")
        content = m.get("content")

        if role == "assistant" and not content and not m.get("tool_calls"):
            continue

        entry = m.copy()
        if "timestamp" not in entry:
            entry["timestamp"] = get_now().isoformat()
        append(entry)

print("Original:", timeit.timeit(original, number=10000))
print("Optimized:", timeit.timeit(optimized, number=10000))
