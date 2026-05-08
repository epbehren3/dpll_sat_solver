# dlis.py - DLIS Decision Heuristic (Dynamic Largest Individual Sum)
# ECE 51216 | Spring 2026 | Behrendt & Morshed
#
# Selects the branching literal that appears most often across all unsatisfied
# clauses. Satisfying that literal directly reduces the most pending clauses,
# shrinking the search space faster than picking arbitrarily.


def clauseSat(clause, assignment):
    # True if any literal in the clause evaluates to True under current assignment
    for literal in clause:
        var = abs(literal)
        if assignment.get(var) is not None:
            value = assignment.get(var) if literal > 0 else not assignment.get(var)
            if value is True:
                return True
    return False


def dlis(clauses, assignment):
    # Count unassigned literal occurrences across all unsatisfied clauses,
    # then return the literal with the highest count as the branching choice.
    counts = {}

    for clause in clauses:
        if clauseSat(clause, assignment):
            continue  # skip already-satisfied clauses

        for literal in clause:
            var = abs(literal)
            if assignment.get(var) is None:
                counts[literal] = counts.get(literal, 0) + 1

    if not counts:
        return None  # all variables assigned

    # Return the literal with the highest occurrence count
    return max(counts, key=counts.__getitem__)
