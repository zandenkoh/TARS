from TARS.utils.helpers import estimate_prompt_tokens

messages = [{"role": "user", "content": "hello", "extra": "field"}, {"role": "assistant", "content": "world"}]
estimate_prompt_tokens(messages)
print("Done")
