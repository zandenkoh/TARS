
def func_list_comp(messages):
    try:
        fast_parts = [m["content"] for m in messages if len(m) == 2 and isinstance(m["content"], str)]
        if len(fast_parts) == len(messages):
            return "\n".join(fast_parts)
    except Exception:
        pass
    return "fallback"

def func_all(messages):
    # What if we use a generator or avoid creating the list if one fails?
    pass
