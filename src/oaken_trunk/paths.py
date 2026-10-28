# SPDX-License-Identifier: Apache-2.0
"""Where Trunk keeps its config, data and runtime files."""

from __future__ import annotations

import os
import stat
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import platformdirs

APP = "oaken-trunk"


class PathError(Exception):
    pass


@dataclass(frozen=True)
class Paths:
    config: Path
    data: Path
    run: Path

    @property
    def config_file(self) -> Path:
        return self.config / "config.toml"

    def ensure(self) -> None:
        for d in (self.config, self.data, self.run):
            ensure_dir(d)


def resolve_paths(environ: Mapping[str, str] = os.environ) -> Paths:
    """``OAKEN_TRUNK_HOME`` if set, else the Linux system layout, else platformdirs (dev)."""
    if home := environ.get("OAKEN_TRUNK_HOME"):
        root = Path(home)
        return Paths(root / "config", root / "data", root / "run")
    if sys.platform.startswith("linux"):
        return Paths(Path("/etc", APP), Path("/var/lib", APP), Path("/run", APP))
    return Paths(
        platformdirs.user_config_path(APP),
        platformdirs.user_data_path(APP),
        platformdirs.user_runtime_path(APP),
    )


def ensure_dir(path: Path) -> Path:
    """Create ``path`` owner-only if missing. Refuse it if it is world-writable."""
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Windows has no POSIX mode bits to check: every directory reports 0o777.
    if os.name == "posix" and path.stat().st_mode & stat.S_IWOTH:
        raise PathError(f"{path} is world-writable; run `chmod o-w {path}` (better: 0700)")
    return path
