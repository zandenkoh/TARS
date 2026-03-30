from pathlib import Path

base = Path("./workspace").resolve()
target_dir = base

f_filename = "../../../etc/passwd"
file_path = target_dir / f_filename

print("Base:", base)
print("File path:", file_path)
print("Resolved file path:", file_path.resolve())

if not str(file_path.resolve()).startswith(str(base)):
    print("Access Denied")
else:
    print("Access Granted")
