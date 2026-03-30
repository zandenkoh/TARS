from pathlib import Path

base = Path("./workspace").resolve()
src = "../workspace/test.txt"
dst = "../../../etc/passwd"

src_path = (base / src).resolve()
dst_path = (base / dst).resolve()

print("src_path:", src_path)
print("dst_path:", dst_path)

if not str(src_path).startswith(str(base.resolve())) or \
   not str(dst_path).startswith(str(base.resolve())):
    print("Access Denied move")
else:
    print("Allowed Move")
