"""
Unit tests for watched_literals and watched_bcp in chaff.py
"""

import pytest
from chaff import watched_literals, watched_bcp


# ─────────────────────────────────────────────────────────────
# watched_literals
# ─────────────────────────────────────────────────────────────

class TestWatchedLiterals:

    def test_all_unassigned_returns_two_watched(self):
        # Two unassigned literals → watch both of them
        clause = [1, 2, 3]
        assignment = {}
        result = watched_literals(clause, assignment)
        assert len(result) == 2
        assert result == [1, 2]

    def test_satisfied_literal_returns_empty(self):
        # x1 is True and literal +1 appears → clause is satisfied
        clause = [1, 2, 3]
        assignment = {1: True}
        result = watched_literals(clause, assignment)
        assert result == []

    def test_satisfied_negative_literal_returns_empty(self):
        # x2 is False and literal -2 appears → clause is satisfied
        clause = [-2, 3]
        assignment = {2: False}
        result = watched_literals(clause, assignment)
        assert result == []

    def test_one_unassigned_one_false_returns_unit(self):
        # x1 is False, x2 unassigned → only x2 watched (unit clause)
        clause = [1, 2]
        assignment = {1: False}
        result = watched_literals(clause, assignment)
        assert result == [2]

    def test_all_false_returns_empty_watched(self):
        # All literals false → no watched literals (conflict scenario)
        clause = [1, 2]
        assignment = {1: False, 2: False}
        result = watched_literals(clause, assignment)
        assert result == []

    def test_single_literal_unassigned(self):
        # A unit clause with no prior assignment
        clause = [5]
        assignment = {}
        result = watched_literals(clause, assignment)
        assert result == [5]

    def test_single_literal_false(self):
        # A unit clause whose literal is already falsified
        clause = [5]
        assignment = {5: False}
        result = watched_literals(clause, assignment)
        assert result == []

    def test_negative_literal_unassigned(self):
        # Clause with only a negative literal, variable unassigned
        clause = [-3]
        assignment = {}
        result = watched_literals(clause, assignment)
        assert result == [-3]


# ─────────────────────────────────────────────────────────────
# watched_bcp
# ─────────────────────────────────────────────────────────────

class TestWatchedBCP:

    def test_unit_clause_forces_positive(self):
        # (-x2) is a unit clause → x2 must be False
        clauses = [[-2]]
        result = watched_bcp(clauses, {})
        assert result is not None
        assert result[2] == False

    def test_unit_clause_forces_negative_literal(self):
        # (x1) forces x1 = True
        clauses = [[1]]
        result = watched_bcp(clauses, {})
        assert result is not None
        assert result[1] == True

    def test_chain_propagation(self):
        # (-x2) → x2=False → (x1 ∨ x2) becomes unit → x1=True
        #                   → (-x1 ∨ x3) becomes unit → x3=True
        clauses = [
            [1, 2],    # x1 ∨ x2
            [-1, 3],   # ¬x1 ∨ x3
            [-2],      # ¬x2  ← seeds the propagation
        ]
        result = watched_bcp(clauses, {})
        assert result is not None
        assert result[2] == False
        assert result[1] == True
        assert result[3] == True

    def test_conflict_returns_none(self):
        # (x1) ∧ (¬x1) → direct conflict
        clauses = [[1], [-1]]
        result = watched_bcp(clauses, {})
        assert result is None

    def test_already_satisfied_clause_skipped(self):
        # x1 is already True; clause [1, 2] is satisfied — no forced assignment
        clauses = [[1, 2]]
        result = watched_bcp(clauses, {1: True})
        assert result is not None
        assert result[1] == True
        assert 2 not in result  # x2 should not be forced

    def test_empty_assignment_no_unit_clauses(self):
        # All clauses have ≥2 unassigned literals → nothing to propagate
        clauses = [[1, 2], [3, 4]]
        result = watched_bcp(clauses, {})
        assert result is not None
        assert result == {}  # assignment unchanged

    def test_partial_assignment_propagates(self):
        # x1=False fed in; clause [1, 2] becomes unit → x2=True
        clauses = [[1, 2]]
        result = watched_bcp(clauses, {1: False})
        assert result is not None
        assert result[2] == True

    def test_all_clauses_already_satisfied(self):
        # Both clauses satisfied by the given assignment
        clauses = [[1, 2], [-3, 4]]
        assignment = {1: True, 3: False}
        result = watched_bcp(clauses, assignment)
        assert result is not None

    def test_does_not_mutate_input_assignment(self):
        # watched_bcp should return a copy, not modify the original
        clauses = [[-1]]
        original = {2: True}
        watched_bcp(clauses, original)
        assert original == {2: True}  # unchanged
