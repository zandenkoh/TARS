import time

messages = [{"role": "user", "content": "Hello world!"} for _ in range(10000)]

def old_fast_path():
    fast_parts = []
    append_fast = fast_parts.append
    for m in messages:
        content = m.get("content")
        if len(m) == 2 and isinstance(content, str):
            append_fast(content)
        else:
            fast_parts = None
            break
    if fast_parts is not None:
        return len(fast_parts)

def new_fast_path():
    fast_parts = [c for m in messages if len(m) == 2 and isinstance(c := m.get("content"), str)]
    if len(fast_parts) == len(messages):
        return len(fast_parts)

t0 = time.perf_counter()
for _ in range(1000):
    old_fast_path()
t1 = time.perf_counter()
print(f"Old: {t1 - t0:.5f}")

t0 = time.perf_counter()
for _ in range(1000):
    new_fast_path()
t1 = time.perf_counter()
print(f"New: {t1 - t0:.5f}")
