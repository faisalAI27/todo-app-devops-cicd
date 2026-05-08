"""
Compatibility shim so ``python todo_app.py`` still works after moving the real
code into the src/todo_app package.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from todo_app.cli import main as _package_main  # type: ignore  # noqa: E402


if __name__ == "__main__":
    _package_main()
