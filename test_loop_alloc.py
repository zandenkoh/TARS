import time


def test_fast_parts(messages):
    start = time.time()
    for _ in range(1000):
        # Current implementation
        try:
            fast_parts = [
                m["content"] for m in messages if len(m) == 2 and isinstance(m["content"], str)
            ]
            if len(fast_parts) == len(messages):
                pass
        except Exception:
            pass
    return time.time() - start


def test_generator(messages):
    start = time.time()
    for _ in range(1000):
        try:
            if all(len(m) == 2 and isinstance(m.get("content"), str) for m in messages):
                fast_parts = [m["content"] for m in messages]
        except Exception:
            pass
    return time.time() - start


def test_early_return(messages):
    start = time.time()
    for _ in range(1000):
        try:
            fast_parts = []
            append = fast_parts.append
            for m in messages:
                content = m.get("content")
                if len(m) == 2 and isinstance(content, str):
                    append(content)
                else:
                    fast_parts = None
                    break
            if fast_parts is not None:
                pass
        except Exception:
            pass
    return time.time() - start


msgs = [{"role": "user", "content": "hi"} for _ in range(100)]
print("list comp:", test_fast_parts(msgs))
print("generator:", test_generator(msgs))
print("early return:", test_early_return(msgs))

# Test with early failure
msgs = (
    [{"role": "user", "content": "hi"} for _ in range(5)]
    + [{"role": "user", "content": "hi", "other": "val"}]
    + [{"role": "user", "content": "hi"} for _ in range(94)]
)
print("list comp (fail):", test_fast_parts(msgs))
print("generator (fail):", test_generator(msgs))
print("early return (fail):", test_early_return(msgs))
