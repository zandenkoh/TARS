import time

from TARS.utils.helpers import estimate_message_tokens

message = {
    "role": "assistant",
    "content": "This is a typical message content. It might be longer, and have some text.",
    "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": '{"location": "London"}'}}],
    "name": "get_weather"
}

start = time.perf_counter()
for _ in range(10000):
    estimate_message_tokens(message)
print(f"Time: {time.perf_counter() - start:.4f}s")
