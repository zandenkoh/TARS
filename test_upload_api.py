from pathlib import Path

base = Path("./workspace").resolve()
target_dir = base
path = "."

target_dir = (base / path).resolve()
if not str(target_dir).startswith(str(base.resolve())):
    print("Access Denied target_dir")

files = [{"filename": "../../../etc/passwd"}]
for file in files:
    file_path = target_dir / file["filename"]
    print("Saving to:", file_path.resolve())
