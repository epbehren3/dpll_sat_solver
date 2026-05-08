# chaff.py - Two-watched-literal BCP
# ECE 51216 | Spring 2026 | Behrendt & Morshed
#
# Implements the watched-literal scheme from the Chaff SAT solver.
# Each clause tracks two "watched" literals. A clause only needs inspection
# when one of its watchers becomes falsified, reducing propagation overhead
# compared to scanning every literal on every assignment change.
#
# Key functions:
#   precompute_watched_literals(clauses)           -> watched_list
#   watched_bcp(clauses, assignment, watched_list) -> assignment | None

from typing import Any


def clause_satisfied(clause, assignment):
    # True if at least one literal in the clause is currently True
    for literal in clause:
        if (literal > 0 and assignment.get(abs(literal)) is True) or \
           (literal < 0 and assignment.get(abs(literal)) is False):
            return True
    return False


def all_clauses_satisfied(clauses, assignment):
    # True only when every clause in the formula is satisfied
    for clause in clauses:
        if not clause_satisfied(clause, assignment):
            return False
    return True


def check_falsified(literal, assignment):
    # True if the literal is explicitly falsified (unassigned literals return False)
    val = assignment.get(abs(literal))
    if val is None:
        return False
    return val is False if literal > 0 else val is True


def precompute_watched_literals(clauses):
    # Initialise the watched list — watch the first two literals of each clause
    return [list(clause[:2]) for clause in clauses]


def update_single_watched(new_assignment, watched):
    # One watcher remains — the clause is unit, so force-assign it
    var = abs(watched[0])
    want_true = watched[0] > 0
    cur = new_assignment.get(var)

    if cur is None:
        new_assignment[var] = want_true
        return new_assignment, True  # new assignment made

    if cur is not want_true:
        return None, False  # contradicts existing assignment — conflict

    return new_assignment, False


def check_literals(clause, assignment, watched, idx_replace):
    # Try to replace a falsified watcher with any non-falsified literal in the clause
    other_lit = watched[1 - idx_replace]
    for literal in clause:
        if literal == other_lit:
            continue
        if not check_falsified(literal, assignment):
            watched[idx_replace] = literal  # update watcher in place
            return assignment, True
    return assignment, False  # no replacement found — clause is now unit


def update_double_watched(new_assignment, clause, watched):
    # Handle the two-watcher case: if a watcher is falsified, find a replacement.
    # If no replacement exists, the clause is unit — force the remaining watcher.
    changed = False

    if check_falsified(watched[0], new_assignment):
        new_assignment, did_replace = check_literals(clause, new_assignment, watched, 0)
        if did_replace:
            changed = True
        else:
            # watched[0] falsified, no replacement — unit on watched[1]
            new_assignment, did_unit = update_single_watched(new_assignment, [watched[1]])
            if new_assignment is None:
                return None, False
            if did_unit:
                changed = True

    elif check_falsified(watched[1], new_assignment):
        new_assignment, did_replace = check_literals(clause, new_assignment, watched, 1)
        if did_replace:
            changed = True
        else:
            # watched[1] falsified, no replacement — unit on watched[0]
            new_assignment, did_unit = update_single_watched(new_assignment, [watched[0]])
            if new_assignment is None:
                return None, False
            if did_unit:
                changed = True

    return new_assignment, changed


def watched_bcp(clauses, assignment, watched_list):
    # Run watched-literal BCP to exhaustion.
    # Iterates until no new assignments are inferred in a full pass.
    # Returns the updated assignment dict, or None on conflict.
    new_assignment = assignment.copy()
    changed = True

    while changed:
        changed = False
        for i, clause in enumerate(clauses):
            watched = watched_list[i]

            if len(watched) == 0:
                # No watchers — conflict if the clause is not already satisfied
                if clause_satisfied(clause, new_assignment):
                    continue
                return None

            elif len(watched) == 1:
                #One watcher remains — the clause is unit, so force-assign it
                new_assignment, did_unit = update_single_watched(new_assignment, watched)
                if new_assignment is None:
                    return None
                if did_unit:
                    changed = True

            else:
                # Two watchers remain — the clause is not unit, so we need to update the watched literals
                new_assignment, did_double = update_double_watched(new_assignment, clause, watched)
                if new_assignment is None:
                    return None
                if did_double:
                    changed = True

    return new_assignment
