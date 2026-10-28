# SPDX-License-Identifier: Apache-2.0
"""The ``steamer`` command: a thin client. Standard library only, so it starts fast."""

from __future__ import annotations


def main(argv: list[str] | None = None) -> int:
    import argparse  # lazy: keep `steamer --version` cheap

    from oaken_trunk import __version__

    parser = argparse.ArgumentParser(prog="steamer", description="Oaken Trunk mail gateway.")
    parser.add_argument("--version", action="version", version=f"steamer {__version__}")
    parser.parse_args(argv)
    parser.print_help()
    return 0
