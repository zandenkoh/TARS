import re
import time

def fast_way2(text, compiled_re):
    matches = []
    for m in compiled_re.finditer(text):
        for g in m.groups():
            if g is not None:
                matches.append(g)
    return matches

text = "ls -la /var/log | grep error > /tmp/output.txt && cat /etc/passwd" * 1000
patterns = [
    r"(?:^|[\s|<>&;\(\)'\"=`,\[\]{}])([A-Za-z]:\\[^\s\"'|<>&;\(\)=`,\[\]{}]+)",
    r"(?:^|[\s|<>&;\(\)'\"=`,\[\]{}])(/[^\s|<>&;\(\)'\"=`,\[\]{}]+)",
    r"(?:^|[\s|<>&;\(\)'\"=`,\[\]{}])(~[^\s|<>&;\(\)'\"=`,\[\]{}]*)"
]
combined_pattern = "|".join(patterns)
compiled_re = re.compile(combined_pattern)

start = time.time()
for _ in range(100):
    fast_way2(text, compiled_re)
print(f"Fast way 2: {time.time() - start:.4f}s")
