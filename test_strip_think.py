import timeit

text = "Hello <think>this is a thought</think> world" * 1000

def original():
    parts = []
    start = 0
    while True:
        start_idx = text.find("<think>", start)
        if start_idx == -1:
            parts.append(text[start:])
            break
        parts.append(text[start:start_idx])
        end_idx = text.find("</think>", start_idx + 7)
        if end_idx == -1:
            break
        start = end_idx + 8
    return "".join(parts).strip()

def optimized():
    chunks = text.split("<think>")
    parts = [chunks[0]]
    append = parts.append
    for chunk in chunks[1:]:
        end_idx = chunk.find("</think>")
        if end_idx != -1:
            append(chunk[end_idx + 8:])
        else:
            break
    return "".join(parts).strip()

print(original() == optimized())
print("Original:", timeit.timeit(original, number=1000))
print("Optimized:", timeit.timeit(optimized, number=1000))
