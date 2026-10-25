# SPDX-License-Identifier: Apache-2.0
"""``move_doc`` moves a file and fixes what refers to it; ``check_prompts`` fails on what it would
have fixed. Both run in a throwaway git repository."""

import subprocess
from pathlib import Path

import move_doc
import pytest

ROOT = Path(__file__).resolve().parents[3]


def repo(tmp_path: Path, files: dict[str, str]) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)  # noqa: S603, S607
    for name, text in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)  # noqa: S603, S607
    return tmp_path


def test_a_move_fixes_links_paths_and_bare_names_and_leaves_the_rest(tmp_path: Path) -> None:
    r = repo(
        tmp_path,
        {
            "docs/prompts/CORE_28-compose.md": (
                "# 28\nSee [rules](CONTEXT.md) and [home](../../README.md).\n"
            ),
            "docs/prompts/CONTEXT.md": "rules\n",
            "docs/prompts/README.md": "| 28 | [compose](CORE_28-compose.md) | x |\nREADME stays.\n",
            "CONTRIBUTING.md": "Run `docs/prompts/CORE_28-compose.md`, i.e. CORE_28-compose.md.\n",
            "README.md": "Not about it. See [rules](docs/prompts/CONTEXT.md).\n",
        },
    )
    out = move_doc.move(r, "docs/prompts/CORE_28-compose.md", "docs/prompts/CORE_28-send.md")
    assert out.moved == ("docs/prompts/CORE_28-compose.md", "docs/prompts/CORE_28-send.md")
    assert (r / "docs/prompts/CORE_28-send.md").is_file()
    assert not (r / "docs/prompts/CORE_28-compose.md").exists()
    assert "(CORE_28-send.md)" in (r / "docs/prompts/README.md").read_text()
    assert "README stays." in (r / "docs/prompts/README.md").read_text()
    text = (r / "CONTRIBUTING.md").read_text()
    assert "`docs/prompts/CORE_28-send.md`" in text and "i.e. CORE_28-send.md." in text
    assert (r / "README.md").read_text().count("CONTEXT.md") == 1  # untouched
    assert out.references == 3 and sorted(out.files) == [
        "CONTRIBUTING.md", "docs/prompts/README.md",
    ]  # fmt: skip


def test_the_moved_files_own_relative_links_still_resolve_from_the_new_place(
    tmp_path: Path,
) -> None:
    r = repo(
        tmp_path,
        {
            "docs/prompts/CORE_28-x.md": "[ctx](CONTEXT.md) [top](../../CONTRIBUTING.md#a)\n",
            "docs/prompts/CONTEXT.md": "c\n",
            "CONTRIBUTING.md": "t\n",
        },
    )
    move_doc.move(r, "docs/prompts/CORE_28-x.md", "docs/archive/CORE_28-x.md")
    moved = (r / "docs/archive/CORE_28-x.md").read_text()
    assert "(../prompts/CONTEXT.md)" in moved and "(../../CONTRIBUTING.md#a)" in moved
    for target in ("../prompts/CONTEXT.md", "../../CONTRIBUTING.md"):
        assert (r / "docs/archive" / target).resolve().is_file()


def test_a_name_other_files_share_is_never_rewritten_by_name(tmp_path: Path) -> None:
    r = repo(
        tmp_path,
        {
            "a/README.md": "# a\n",
            "b/README.md": "# b\nsee README.md\n",
            "docs/linker.md": "[a](../a/README.md) and README.md\n",
        },
    )
    move_doc.move(r, "a/README.md", "a/INTRO.md")
    text = (r / "docs/linker.md").read_text()
    assert "(../a/INTRO.md)" in text and "and README.md" in text  # the bare name is ambiguous
    assert "see README.md" in (r / "b/README.md").read_text()


def test_a_move_never_overwrites_and_needs_a_file(tmp_path: Path) -> None:
    r = repo(tmp_path, {"a.md": "a\n", "b.md": "b\n"})
    with pytest.raises(move_doc.MoveError, match="already exists"):
        move_doc.move(r, "a.md", "b.md")
    with pytest.raises(move_doc.MoveError, match="is not a file"):
        move_doc.move(r, "nope.md", "c.md")
    assert (r / "a.md").read_text() == "a\n" and (r / "b.md").read_text() == "b\n"


def test_a_dry_run_changes_nothing_and_still_counts(tmp_path: Path) -> None:
    r = repo(tmp_path, {"docs/x.md": "x\n", "docs/y.md": "[x](x.md)\n"})
    out = move_doc.move(r, "docs/x.md", "docs/z.md", dry_run=True)
    assert out.references == 1 and (r / "docs/x.md").is_file() and not (r / "docs/z.md").exists()
    assert (r / "docs/y.md").read_text() == "[x](x.md)\n"
