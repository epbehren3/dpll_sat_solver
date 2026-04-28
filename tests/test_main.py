"""Integration-style unit tests for main.py (CLI path, DIMACS load, DPLL, metrics)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import grabMetrics
import pytest

import main as main_mod


def _write_cnf(path: Path, body: str) -> str:
    path.write_text(body.strip() + "\n", encoding="ascii")
    return str(path.resolve())


def _intense_sat_dimacs() -> str:
    """SAT: long Horn chain (forces x1..x20) plus five independent 'exactly-one' pairs (21–30)."""
    clauses: list[list[int]] = [[1]]
    clauses.extend([[-i, i + 1] for i in range(1, 20)])
    v = 21
    while v <= 29:
        clauses.append([v, v + 1])
        clauses.append([-v, -(v + 1)])
        v += 2
    n_vars = 30
    lines = [f"p cnf {n_vars} {len(clauses)}"]
    lines.extend(" ".join(map(str, c)) + " 0" for c in clauses)
    return "\n".join(lines)


def _pigeonhole_3_2_unsat_dimacs() -> str:
    """UNSAT: 3 pigeons, 2 holes (variables 1..6 = pigeon i in hole j)."""
    clauses = [
        [1, 2],
        [3, 4],
        [5, 6],
        [-1, -3],
        [-1, -5],
        [-3, -5],
        [-2, -4],
        [-2, -6],
        [-4, -6],
    ]
    lines = ["p cnf 6 9"]
    lines.extend(" ".join(map(str, c)) + " 0" for c in clauses)
    return "\n".join(lines)


class TestMainPipeline:
    def test_main_reports_sat_for_unit_clause(self, tmp_path: Path, capsys) -> None:
        cnf = _write_cnf(
            tmp_path / "sat.cnf",
            """
            p cnf 1 1
            1 0
            """,
        )
        with patch.object(main_mod.metrics, "report"):
            main_mod.main(argv=["prog", cnf])
        captured = capsys.readouterr().out
        assert "True" in captured

    def test_main_reports_unsat_for_contradiction(self, tmp_path: Path, capsys) -> None:
        cnf = _write_cnf(
            tmp_path / "unsat.cnf",
            """
            p cnf 1 2
            1 0
            -1 0
            """,
        )
        with patch.object(main_mod.metrics, "report"):
            main_mod.main(argv=["prog", cnf])
        captured = capsys.readouterr().out
        assert "False" in captured

    def test_main_tiny_sat_two_vars(self, tmp_path: Path, capsys) -> None:
        cnf = _write_cnf(
            tmp_path / "sat2.cnf",
            """
            p cnf 2 2
            1 2 0
            -1 2 0
            """,
        )
        with patch.object(main_mod.metrics, "report"):
            main_mod.main(argv=["prog", cnf])
        captured = capsys.readouterr().out
        assert "True" in captured

    def test_main_records_metrics_when_report_runs(self, tmp_path: Path, capsys) -> None:
        cnf = _write_cnf(tmp_path / "m.cnf", "p cnf 1 1\n1 0\n")
        log = tmp_path / "metrics.txt"
        with patch.object(grabMetrics, "logpath", str(log)):
            main_mod.main(argv=["prog", cnf])
        text = log.read_text(encoding="ascii")
        assert "Wall Time:" in text
        assert "CPU Time:" in text
        assert "Peak Memory:" in text
        assert "Result: SAT" in text

    def test_main_intense_sat_chain_and_xor_blocks(self, tmp_path: Path, capsys) -> None:
        cnf = _write_cnf(tmp_path / "intense_sat.cnf", _intense_sat_dimacs())
        with patch.object(main_mod.metrics, "report"):
            main_mod.main(argv=["prog", cnf])
        out = capsys.readouterr().out
        assert "True" in out

    def test_main_intense_unsat_pigeonhole_3_2(self, tmp_path: Path, capsys) -> None:
        cnf = _write_cnf(tmp_path / "php32.cnf", _pigeonhole_3_2_unsat_dimacs())
        with patch.object(main_mod.metrics, "report"):
            main_mod.main(argv=["prog", cnf])
        out = capsys.readouterr().out
        assert "False" in out


class TestMainCLI:
    def test_module_invocation_requires_path(self) -> None:
        with pytest.raises(IndexError):
            main_mod.main(argv=["prog"])
