from pathlib import Path

base = Path("./workspace").resolve()
target_dir = base
file_name = "../../../etc/passwd"

print("Before Path check:")
try:
    if not str(target_dir).startswith(str(base.resolve())):
        print("Denied 1")
    file_path = target_dir / file_name
    print("Resolved path:", file_path.resolve())
except Exception as e:
    print("Error:", e)
