# dpll.py - DPLL SAT Solver with configurable heuristics
#
import chaff
import dlis



def dpll(clauses, assignment, watched_list=None):
    #build watched list if not provided by the caller
    if watched_list is None:
        watched_list = chaff.precompute_watched_literals(clauses)

    # Infer all forced assignments; None means a conflict was detected

    new_assignment = chaff.watched_bcp(clauses, assignment, watched_list)

    if new_assignment is None:
        return False  # conflict — backtrack

    if chaff.all_clauses_satisfied(clauses, new_assignment):
        assignment.update(new_assignment)  # write solution back to caller's dict
        return True

    # Pick the next literal to branch on using the configured heuristic
    literal = dlis.dlis(clauses, new_assignment)

    if literal is None:
        return False  # no unassigned literals but formula unsatisfied — contradiction

    var = abs(literal)

    # Branch True: try the literal's natural polarity
    new_assignment[var] = (literal > 0)
    next_watched = [w[:] for w in watched_list] if watched_list is not None else None
    if dpll(clauses, new_assignment, next_watched):
        assignment.update(new_assignment)  # propagate solution back up the call stack
        return True

    # Branch False: try the opposite polarity (chronological backtracking)
    new_assignment[var] = (literal <= 0)
    next_watched = [w[:] for w in watched_list] if watched_list is not None else None
    if dpll(clauses, new_assignment, next_watched):
        assignment.update(new_assignment)  # propagate solution back up the call stack
        return True

    return False  # both branches exhausted — UNSAT on this path
