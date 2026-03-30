
import os
import tempfile
from pathlib import Path

def test_path_traversal_vulnerability():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir).resolve()
        base_dir = tmpdir_path / "workspace"
        base_dir.mkdir()

        secret_dir = tmpdir_path / "workspace_secret"
        secret_dir.mkdir()

        # This simulates the vulnerable logic in api.py
        def is_safe_vulnerable(path_str, base_path):
            target_path = (base_path / path_str).resolve()
            return str(target_path).startswith(str(base_path.resolve()))

        path_str = "../workspace_secret"
        vulnerable = is_safe_vulnerable(path_str, base_dir)
        print(f"Vulnerable check for {path_str}: {vulnerable}")
        if vulnerable:
            print("Vulnerability confirmed!")
        else:
            print("Vulnerability NOT confirmed!")

def test_path_traversal_fix():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir).resolve()
        base_dir = tmpdir_path / "workspace"
        base_dir.mkdir()

        def is_safe_fixed(path_str, base_path):
            try:
                target_path = (base_path / path_str).resolve()
                return target_path.is_relative_to(base_path.resolve())
            except ValueError:
                return False

        path_str = "../workspace_secret"
        safe = is_safe_fixed(path_str, base_dir)
        print(f"Fixed check for {path_str}: {safe}")
        if not safe:
            print("Fix confirmed!")
        else:
            print("Fix failed!")

if __name__ == "__main__":
    test_path_traversal_vulnerability()
    test_path_traversal_fix()
