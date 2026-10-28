# SPDX-License-Identifier: Apache-2.0
"""Every Python file (tracked or new) starts with the SPDX header."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = "# SPDX-License-Identifier: Apache-2.0"


def _python_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "*.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return sorted({p for p in out.split("\0") if p and (ROOT / p).is_file()})


def missing_header(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()[:2]
    if lines and lines[0].startswith("#!"):
        lines = lines[1:]
    return not lines or lines[0] != HEADER


def test_every_python_file_has_the_header() -> None:
    files = _python_files()
    assert files
    assert [f for f in files if missing_header(ROOT / f)] == []


def test_missing_header_is_caught(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("import os\n", encoding="utf-8")
    assert missing_header(bad)
    bad.write_text(f"#!/usr/bin/env python3\n{HEADER}\n", encoding="utf-8")
    assert not missing_header(bad)
