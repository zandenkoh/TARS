import time
import json
import uuid
import sys

def estimate_old(messages):
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
        return 1

def estimate_new(messages):
    fast_parts = [c for m in messages if len(m) == 2 and type(c := m.get("content")) is str]
    if len(fast_parts) == len(messages):
        return 1

messages = [{"role": "user", "content": f"hello world {i}"} for i in range(1000)]

# warmup
for _ in range(1000):
    estimate_old(messages)
    estimate_new(messages)

n = 10000
t0 = time.perf_counter()
for _ in range(n):
    estimate_old(messages)
t1 = time.perf_counter()

t2 = time.perf_counter()
for _ in range(n):
    estimate_new(messages)
t3 = time.perf_counter()

print(f"Old: {t1-t0:.4f}s")
print(f"New: {t3-t2:.4f}s")
