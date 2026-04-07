import time
import json
import uuid
import sys
import tiktoken

_TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

def estimate_old(messages):
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
            return len(_TIKTOKEN_ENC.encode("\n".join(fast_parts))) + len(messages) * 4
    except Exception:
        pass
    return 0

def estimate_new(messages):
    try:
        fast_parts = [c for m in messages if len(m) == 2 and type(c := m.get("content")) is str]
        if len(fast_parts) == len(messages):
            return len(_TIKTOKEN_ENC.encode("\n".join(fast_parts))) + len(messages) * 4
    except Exception:
        pass
    return 0

def estimate_gen(messages):
    try:
        # Avoid list comprehension memory allocation if one fails
        if all(len(m) == 2 and type(m.get("content")) is str for m in messages):
            fast_parts = [m["content"] for m in messages]
            return len(_TIKTOKEN_ENC.encode("\n".join(fast_parts))) + len(messages) * 4
    except Exception:
        pass
    return 0

messages_success = [{"role": "user", "content": f"hello world {i}"} for i in range(1000)]
messages_fail = [{"role": "user", "content": f"hello world {i}"} for i in range(10)] + [{"role": "user", "content": f"hello world {i}", "extra": "val"} for i in range(990)]

n = 10000

t0 = time.perf_counter()
for _ in range(n): estimate_old(messages_success)
t1 = time.perf_counter()

t2 = time.perf_counter()
for _ in range(n): estimate_new(messages_success)
t3 = time.perf_counter()

t4 = time.perf_counter()
for _ in range(n): estimate_gen(messages_success)
t5 = time.perf_counter()

print("--- Success ---")
print(f"Old: {t1-t0:.4f}s")
print(f"New: {t3-t2:.4f}s")
print(f"Gen: {t5-t4:.4f}s")

t0 = time.perf_counter()
for _ in range(n): estimate_old(messages_fail)
t1 = time.perf_counter()

t2 = time.perf_counter()
for _ in range(n): estimate_new(messages_fail)
t3 = time.perf_counter()

t4 = time.perf_counter()
for _ in range(n): estimate_gen(messages_fail)
t5 = time.perf_counter()

print("--- Fail early ---")
print(f"Old: {t1-t0:.4f}s")
print(f"New: {t3-t2:.4f}s")
print(f"Gen: {t5-t4:.4f}s")
