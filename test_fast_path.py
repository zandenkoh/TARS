import time
import json
from TARS.utils.helpers import estimate_prompt_tokens, _get_tiktoken_encoding

messages = [
    {"role": "user", "content": "hello"}
] * 1000

start = time.time()
for _ in range(100):
    estimate_prompt_tokens(messages)
orig_time = time.time() - start

def estimate_prompt_tokens_opt(messages, tools=None):
    try:
        enc = _get_tiktoken_encoding()

        # Fast path
        if not tools:
            try:
                fast_parts = []
                append_fast = fast_parts.append
                for m in messages:
                    if len(m) == 2 and isinstance(content := m.get("content"), str):
                        append_fast(content)
                    else:
                        fast_parts = None
                        break
                if fast_parts is not None:
                    return len(enc.encode("\n".join(fast_parts))) + len(messages) * 4
            except Exception:
                pass
        return 0
    except Exception:
        return 0

start = time.time()
for _ in range(100):
    estimate_prompt_tokens_opt(messages)
opt_time = time.time() - start

print(f"Original: {orig_time}")
print(f"Optimized: {opt_time}")
