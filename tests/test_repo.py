# SPDX-License-Identifier: Apache-2.0
"""Repo-wide guards: no mail, data or secrets tracked, and .gitignore covers each kind."""

from __future__ import annotations

import re
import subprocess
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath

import pytest

ROOT = Path(__file__).resolve().parent.parent

SENSITIVE = [
    "*.db",
    "*.eml",
    "*.mbox",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.private",
    "*.gpg",
    "secring.*",
    "token*.json",
    "credentials*.json",
    "config.toml",
]
ALLOWED = {".env.example"}

# One sample path per pattern, plus one under a spool directory. Each must be ignored.
SAMPLES = [
    "x.db",
    "x.eml",
    "x.mbox",
    ".env",
    ".env.local",
    "server.pem",
    "server.key",
    "x.p12",
    "x.pfx",
    "dkim/default.private",
    "signing.gpg",
    "secring.gpg",
    "token.json",
    "credentials.json",
    "config.toml",
    "config/config.toml",
    "data/spool/new/1",
    "spool/x",
]


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def sensitive(path: str) -> bool:
    p = PurePosixPath(path)
    if p.name in ALLOWED:
        return False
    if "spool" in p.parts[:-1] and p.parts[0] != "src":
        return True
    return any(fnmatchcase(p.name, pat) for pat in SENSITIVE)


def test_no_sensitive_file_is_tracked() -> None:
    tracked = _git("ls-files", "-z").stdout.split("\0")
    assert [p for p in tracked if p and sensitive(p)] == []


@pytest.mark.parametrize("sample", SAMPLES)
def test_gitignore_covers(sample: str) -> None:
    assert sensitive(sample)
    assert _git("check-ignore", "-q", "--no-index", sample).returncode == 0, sample


def test_env_example_is_not_ignored() -> None:
    assert _git("check-ignore", "-q", "--no-index", ".env.example").returncode == 1


def test_workflow_actions_are_pinned_by_sha() -> None:
    for workflow in (ROOT / ".github/workflows").glob("*.y*ml"):
        for line in workflow.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(("uses:", "- uses:")):
                ref = line.split("uses:", 1)[1].split("#", 1)[0].strip()
                assert re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", ref), f"{workflow}: {ref}"
