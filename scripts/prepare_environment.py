"""Optional clean standalone venv bootstrap. Run only after installation approval.

Creates the explicitly requested project-local D:\\APOLLO\\.venv, without installing
application dependencies or linking workshop packages. Never overwrites a venv.
"""
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    if root != Path(r"D:\APOLLO"):
        raise SystemExit("Run this bootstrap from the migrated APOLLO project")
    destination = Path(r"D:\APOLLO\.venv")
    if destination.exists():
        raise SystemExit("Environment exists; inspect it instead of overwriting")
    subprocess.run(
        [sys.executable, "-B", "-m", "venv", str(destination)], check=True
    )
    print("Created standalone APOLLO environment; no workshop package bridge.")


if __name__ == "__main__":
    main()


