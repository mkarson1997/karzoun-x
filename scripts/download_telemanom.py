from __future__ import annotations

import pathlib
import shutil
import subprocess

UPSTREAM = "https://github.com/khundman/telemanom.git"
DESTINATION = pathlib.Path("data/raw/telemanom")


def main() -> int:
    if shutil.which("git") is None:
        raise SystemExit("git is required to acquire the upstream Telemanom repository")
    if DESTINATION.exists():
        raise SystemExit(f"Destination already exists: {DESTINATION}")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", UPSTREAM, str(DESTINATION)],
        check=True,
    )
    print(f"Cloned upstream research repository to {DESTINATION}")
    print("Review upstream licensing/citation terms before redistributing data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
