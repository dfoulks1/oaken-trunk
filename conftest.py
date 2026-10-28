# SPDX-License-Identifier: Apache-2.0
"""Every test gets its own OAKEN_TRUNK_HOME and no other OAKEN_TRUNK_* variable."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_home(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> Path:
    for name in list(os.environ):
        if name.startswith("OAKEN_TRUNK_"):
            monkeypatch.delenv(name)
    home = tmp_path_factory.mktemp("oaken_trunk_home")
    monkeypatch.setenv("OAKEN_TRUNK_HOME", str(home))
    return home
