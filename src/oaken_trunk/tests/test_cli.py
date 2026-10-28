# SPDX-License-Identifier: Apache-2.0
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from oaken_trunk import __version__
from oaken_trunk.cli import main


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"steamer {__version__}"


def test_no_arguments_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage: steamer" in capsys.readouterr().out


def test_steamer_and_python_m_print_the_same_version() -> None:
    steamer = shutil.which("steamer", path=str(Path(sys.executable).parent))
    assert steamer, "the steamer console script is not installed"
    for cmd in ([steamer, "--version"], [sys.executable, "-m", "oaken_trunk", "--version"]):
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        assert out.stdout.strip() == f"steamer {__version__}"
