import time
import json
import uuid
import sys
import tiktoken

_TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

def estimate_isinstance(messages):
    try:
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
    except Exception:
        pass
    return 0

def estimate_type(messages):
    try:
        fast_parts = []
        append_fast = fast_parts.append
        for m in messages:
            content = m.get("content")
            if len(m) == 2 and type(content) is str:
                append_fast(content)
            else:
                fast_parts = None
                break
        if fast_parts is not None:
            return 1
    except Exception:
        pass
    return 0


messages_success = [{"role": "user", "content": f"hello world {i}"} for i in range(1000)]
messages_fail = [{"role": "user", "content": f"hello world {i}"} for i in range(10)] + [{"role": "user", "content": f"hello world {i}", "extra": "val"} for i in range(990)]

n = 10000

t0 = time.perf_counter()
for _ in range(n): estimate_isinstance(messages_success)
t1 = time.perf_counter()

t2 = time.perf_counter()
for _ in range(n): estimate_type(messages_success)
t3 = time.perf_counter()

print("--- Success ---")
print(f"Isinstance: {t1-t0:.4f}s")
print(f"Type is: {t3-t2:.4f}s")

t0 = time.perf_counter()
for _ in range(n): estimate_isinstance(messages_fail)
t1 = time.perf_counter()

t2 = time.perf_counter()
for _ in range(n): estimate_type(messages_fail)
t3 = time.perf_counter()

print("--- Fail early ---")
print(f"Isinstance: {t1-t0:.4f}s")
print(f"Type is: {t3-t2:.4f}s")
