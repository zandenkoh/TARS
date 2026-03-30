from pathlib import Path

base = Path("/app/workspace").resolve()
target = Path("/app/workspace2").resolve()

print(str(target).startswith(str(base)))
print(target.is_relative_to(base))

