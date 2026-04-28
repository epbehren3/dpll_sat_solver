#!/usr/bin/env python3
"""Run the DPLL driver on a DIMACS .cnf (SATLIB layouts supported)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import main as main_mod


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def main() -> None:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description="Run main.main() on a DIMACS CNF file.",
    )
    parser.add_argument(
        "cnf",
        nargs="?",
        type=Path,
        default=root / "satlib" / "uf20-01.cnf",
        help="Path to .cnf (default: satlib/uf20-01.cnf)",
    )
    args = parser.parse_args()
    cnf = args.cnf if args.cnf.is_absolute() else (root / args.cnf).resolve()
    if not cnf.is_file():
        sys.exit(f"Not a file: {cnf}")
    main_mod.main(argv=[sys.argv[0], str(cnf)])


if __name__ == "__main__":
    main()
