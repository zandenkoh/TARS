import shutil
from pathlib import Path

base = Path("./workspace").resolve()
src = "test.txt"
dst = "../../../etc/passwd"

src_path = (base / src).resolve()
dst_path = (base / dst).resolve()

if dst_path.exists() and dst_path.is_dir():
    dst_path = dst_path / src_path.name
