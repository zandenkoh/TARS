import json
import time

from TARS.utils.helpers import _get_tiktoken_encoding


def estimate_message_tokens_optimized(message):
    try:
        # Fast path for simple messages (e.g. role + content string)
        if len(message) == 2 and isinstance(content := message.get("content"), str):
            if not content:
                return 4
            enc = _get_tiktoken_encoding()
            return max(4, len(enc.encode(content)) + 4)
    except Exception:
        pass

    content = message.get("content")
    parts = []
    append = parts.append
    dumps = json.dumps

    if isinstance(content, str):
        append(content)
    elif isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text = part.get("text", "")
                if text:
                    append(text)
            else:
                append(dumps(part, ensure_ascii=False))
    elif content is not None:
        append(dumps(content, ensure_ascii=False))

    for key in ("name", "tool_call_id"):
        value = message.get(key)
        if isinstance(value, str) and value:
            append(value)

    tc = message.get("tool_calls")
    if tc:
        append(dumps(tc, ensure_ascii=False))

    rc = message.get("reasoning_content")
    if isinstance(rc, str) and rc:
        append(rc)

    payload = "\n".join(parts)
    if not payload:
        return 4
    try:
        enc = _get_tiktoken_encoding()
        return max(4, len(enc.encode(payload)) + 4)
    except Exception:
        return max(4, len(payload) // 4 + 4)

message = {
    "role": "assistant",
    "content": "This is a typical message content. It might be longer, and have some text.",
    "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": '{"location": "London"}'}}],
    "name": "get_weather"
}

start = time.perf_counter()
for _ in range(10000):
    estimate_message_tokens_optimized(message)
print(f"Time optimized: {time.perf_counter() - start:.4f}s")
