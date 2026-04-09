import re
import time

def slow_way(text):
    win = _WIN_PATH_RE.findall(text)
    posix = _POSIX_PATH_RE.findall(text)
    home = _HOME_PATH_RE.findall(text)
    return win + posix + home

def fast_way(text):
    return _ABS_PATH_RE.findall(text)

_WIN_PATH_RE = re.compile(r"(?:^|[\s|<>&;\(\)'\"=`,\[\]{}])([A-Za-z]:\\[^\s\"'|<>&;\(\)=`,\[\]{}]+)")
_POSIX_PATH_RE = re.compile(r"(?:^|[\s|<>&;\(\)'\"=`,\[\]{}])(/[^\s|<>&;\(\)'\"=`,\[\]{}]+)")
_HOME_PATH_RE = re.compile(r"(?:^|[\s|<>&;\(\)'\"=`,\[\]{}])(~[^\s|<>&;\(\)'\"=`,\[\]{}]*)")

_ABS_PATH_RE = re.compile(r"(?:^|[\s|<>&;\(\)'\"=`,\[\]{}])([A-Za-z]:\\[^\s\"'|<>&;\(\)=`,\[\]{}]+|/[^\s|<>&;\(\)'\"=`,\[\]{}]+|~[^\s|<>&;\(\)'\"=`,\[\]{}]*)")

text = "ls -la /var/log | grep error > /tmp/output.txt && cat /etc/passwd && echo ~jules/hi && C:\\Windows\\System32\\cmd.exe " * 1000

start = time.time()
for _ in range(100):
    slow_way(text)
print(f"Slow way: {time.time() - start:.4f}s")

start = time.time()
for _ in range(100):
    fast_way(text)
print(f"Fast way: {time.time() - start:.4f}s")

assert sorted(slow_way(text)) == sorted(fast_way(text))
