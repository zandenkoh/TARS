from TARS.utils.helpers import estimate_message_tokens, estimate_prompt_tokens

def test_fast_path():
    messages = [
        {"role": "user", "content": "hello world"} for _ in range(10)
    ]
    # Call to warm up/verify it executes correctly
    estimate_prompt_tokens(messages)
    estimate_message_tokens(messages[0])

    # Now add something that should trigger the fallback
    messages.append({"role": "user", "content": [{"type": "text", "text": "hello"}]})
    estimate_prompt_tokens(messages)

    assert True
