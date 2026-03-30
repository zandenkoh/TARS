import shutil
from pathlib import Path

base = Path("./workspace").resolve()
base.mkdir(exist_ok=True)
src = "test.txt"
dst = "."

src_path = (base / src).resolve()
src_path.write_text("hello")
dst_path = (base / dst).resolve()

if dst_path.exists() and dst_path.is_dir():
    dst_path = dst_path / src_path.name

print("Moving to:", dst_path)
