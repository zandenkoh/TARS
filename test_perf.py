import time
import json
from TARS.utils.helpers import estimate_prompt_tokens, estimate_prompt_tokens_chain

messages = [
    {"role": "user", "content": "hello"}
] * 1000

start = time.time()
for _ in range(100):
    estimate_prompt_tokens(messages)
print("Without tools:", time.time() - start)

messages_with_tools = [
    {"role": "user", "content": "hello"},
    {"role": "assistant", "tool_calls": [{"id": "1", "type": "function", "function": {"name": "test"}}]},
    {"role": "tool", "tool_call_id": "1", "name": "test", "content": "result"}
] * 333

start = time.time()
for _ in range(100):
    estimate_prompt_tokens(messages_with_tools, tools=[])
print("With tools:", time.time() - start)
