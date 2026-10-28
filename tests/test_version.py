# SPDX-License-Identifier: Apache-2.0
"""``oaken_trunk.__version__`` is the one source of the version."""

from __future__ import annotations

import re
import tomllib
from importlib import metadata
from pathlib import Path
from typing import Any

import oaken_trunk

ROOT = Path(__file__).resolve().parent.parent
VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)(\S*)")


def _toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _release(version: str) -> tuple[tuple[int, ...], bool]:
    m = VERSION.fullmatch(version)
    assert m, f"not a version: {version}"
    return tuple(int(x) for x in m.groups()[:3]), not m.group(4)


def test_init_states_it_once() -> None:
    text = (ROOT / "src/oaken_trunk/__init__.py").read_text(encoding="utf-8")
    assert len(re.findall(r"^__version__ = ", text, re.M)) == 1
    _release(oaken_trunk.__version__)


def test_root_reads_it_from_init() -> None:
    root = _toml(ROOT / "pyproject.toml")
    assert "version" not in root["project"]
    assert "version" in root["project"]["dynamic"]
    assert root["tool"]["hatch"]["version"]["path"] == "src/oaken_trunk/__init__.py"


def test_workspace_members_agree() -> None:
    members = _toml(ROOT / "pyproject.toml")["tool"]["uv"]["workspace"]["members"]
    for pattern in members:
        for pyproject in ROOT.glob(f"{pattern}/pyproject.toml"):
            stated = _toml(pyproject)["project"].get("version")
            assert stated in (None, oaken_trunk.__version__), pyproject


def test_built_metadata_agrees() -> None:
    assert metadata.version("oaken-trunk") == oaken_trunk.__version__


def test_changelog_agrees() -> None:
    current, final = _release(oaken_trunk.__version__)
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    headings = [_release(v)[0] for v in re.findall(r"^## \[(\d[^\]]*)\]", text, re.M)]
    assert all(h <= current for h in headings), "CHANGELOG names a version newer than __version__"
    if final:
        assert current in headings, "a released __version__ needs its CHANGELOG heading"


def test_docs_group_is_not_a_runtime_dependency() -> None:
    docs = _toml(ROOT / "pyproject.toml")["dependency-groups"]["docs"]
    names = {re.split(r"[<>=!~;\[ ]", d, maxsplit=1)[0].lower() for d in docs}
    required = metadata.requires("oaken-trunk") or []
    runtime = {re.split(r"[<>=!~;\[ ]", r, maxsplit=1)[0].lower() for r in required}
    assert not names & runtime
