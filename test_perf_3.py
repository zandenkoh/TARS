import time

from TARS.utils.helpers import estimate_prompt_tokens

messages = [{"role": "user", "content": "hello"}] * 50

start = time.perf_counter()
for _ in range(5000):
    estimate_prompt_tokens(messages)
print(f"Time original: {time.perf_counter() - start:.4f}s")
