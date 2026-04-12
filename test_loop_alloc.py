import time

def test_for_loop(msgs):
    start = time.time()
    for _ in range(1000):
        for msg in msgs:
            for key in ("name", "tool_call_id"):
                value = msg.get(key)
                if isinstance(value, str) and value:
                    pass
    return time.time() - start

def test_walrus(msgs):
    start = time.time()
    for _ in range(1000):
        for msg in msgs:
            if value := msg.get("name"):
                if isinstance(value, str):
                    pass
            if value := msg.get("tool_call_id"):
                if isinstance(value, str):
                    pass
    return time.time() - start

msgs = [{"role": "assistant", "content": "hi", "name": "foo", "tool_call_id": "bar"} for _ in range(100)]
print("for loop:", test_for_loop(msgs))
print("walrus:", test_walrus(msgs))
