from pathlib import Path
base = Path("/app/workspace")
target_dir = base / "."
target_dir = target_dir.resolve()
file_name = "../../../etc/passwd"
file_path = target_dir / file_name

print("Resolved base:", base.resolve())
print("Resolved target_dir:", target_dir)
print("Resolved file_path:", file_path.resolve())

if not str(file_path.resolve()).startswith(str(base.resolve())):
    print("Access Denied file_path")
