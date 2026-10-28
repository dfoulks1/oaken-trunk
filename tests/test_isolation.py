# SPDX-License-Identifier: Apache-2.0
import os
from pathlib import Path


def test_home_is_a_private_temp_dir() -> None:
    home = Path(os.environ["OAKEN_TRUNK_HOME"])
    assert home.is_dir()
    assert not any(home.iterdir())


def test_only_home_is_set() -> None:
    assert [n for n in os.environ if n.startswith("OAKEN_TRUNK_")] == ["OAKEN_TRUNK_HOME"]
