from fastapi import FastAPI, UploadFile, File
import shutil
from pathlib import Path

target_dir = Path("./workspace")
target_dir.mkdir(exist_ok=True)

class MockFile:
    def __init__(self, filename):
        self.filename = filename

f = MockFile("../../../etc/passwd")

# simulation of what TARS does
try:
    file_path = target_dir / f.filename
    print("Resolved path:", file_path.resolve())
except Exception as e:
    print("Error:", e)
