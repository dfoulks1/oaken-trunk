# SPDX-License-Identifier: Apache-2.0
"""Each import-linter contract in pyproject.toml catches its violation, on a throwaway tree."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONFIG = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"][
    "importlinter"
]
CLEAN = {
    "oaken_trunk/__init__.py": "",
    "oaken_trunk/cli.py": "",
    "oaken_trunk/__main__.py": "import oaken_trunk.cli\n",
    "oaken_trunk/testing/__init__.py": "",
    "oaken_trunk/tests/__init__.py": "",
    "oaken_trunk/tests/test_x.py": "import oaken_trunk.testing\nimport oaken_trunk.cli\n",
    "oaken_trunk_a/__init__.py": "",
    "oaken_trunk_b/__init__.py": "",
}


def _toml(value: object) -> str:
    # The config holds only strings, booleans and lists of strings; JSON spells those as TOML does.
    return json.dumps(value)


def _lint(tmp_path: Path, extra: dict[str, str]) -> subprocess.CompletedProcess[str]:
    for rel, text in {**CLEAN, **extra}.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    lines = ["[tool.importlinter]"]
    for key, value in CONFIG.items():
        if key == "root_packages":
            value = [*value, "oaken_trunk_a", "oaken_trunk_b"]
        if key != "contracts":
            lines.append(f"{key} = {_toml(value)}")
    for contract in CONFIG["contracts"]:
        lines.append("[[tool.importlinter.contracts]]")
        lines += [f"{key} = {_toml(value)}" for key, value in contract.items()]
    (tmp_path / "pyproject.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    lint = shutil.which("lint-imports", path=str(Path(sys.executable).parent))
    assert lint, "lint-imports is not installed"
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(tmp_path), str(ROOT)])}
    return subprocess.run(
        [lint, "--no-cache"], cwd=tmp_path, env=env, capture_output=True, text=True
    )


def test_clean_tree_passes(tmp_path: Path) -> None:
    result = _lint(tmp_path, {})
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("contract", "rel", "text"),
    [
        ("Core never imports a plugin", "oaken_trunk/engine.py", "import oaken_trunk_x\n"),
        ("Core never imports a plugin", "oaken_trunk/engine.py", "import oaken_trunk_a\n"),
        ("Core never imports a client", "oaken_trunk/engine.py", "import oaken_trunk.cli\n"),
        ("A plugin never imports another plugin", "oaken_trunk_a/x.py", "import oaken_trunk_b\n"),
        ("A plugin never imports another plugin", "oaken_trunk_a/x.py", "import oaken_trunk_z\n"),
        (
            "Nothing imports oaken_trunk.testing outside tests",
            "oaken_trunk/engine.py",
            "from oaken_trunk import testing\n",
        ),
        (
            "Nothing imports oaken_trunk.testing outside tests",
            "oaken_trunk_a/x.py",
            "import oaken_trunk.testing\n",
        ),
    ],
)
def test_violation_is_caught(tmp_path: Path, contract: str, rel: str, text: str) -> None:
    names = {c["name"] for c in CONFIG["contracts"]}
    assert contract in names
    result = _lint(tmp_path, {rel: text})
    assert result.returncode != 0
    assert f"{contract} BROKEN" in result.stdout, result.stdout + result.stderr
    assert result.stdout.count("BROKEN") == 1, result.stdout
