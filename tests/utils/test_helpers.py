from TARS.utils.helpers import estimate_prompt_tokens, estimate_message_tokens

def test_estimate_prompt_tokens_fast_path():
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
    ]
    tokens = estimate_prompt_tokens(messages)
    assert tokens > 0

def test_estimate_prompt_tokens_slow_path():
    messages = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {"role": "assistant", "content": "Hi"}
    ]
    tokens = estimate_prompt_tokens(messages)
    assert tokens > 0

def test_estimate_message_tokens():
    msg = {"role": "user", "content": "Hello"}
    tokens = estimate_message_tokens(msg)
    assert tokens > 0
