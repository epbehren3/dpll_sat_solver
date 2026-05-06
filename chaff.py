#Watched literals

#IF watched literals are not false, then the clause is satisfied and not a unit clause

# If one of the two literals is false, then we look for another literal in the clause that is not false to watch instead.

#If we find one, we update the watched literals and continue. If we cannot find a new literal to watch,

# then the clause becomes a unit clause, and we can infer the value of the remaining unassigned literal.

#Once we determine there is only one unassigned literal left in the clause. We infer a value that satisfied the literal

# and run BCP to propagate the consequences of this assignment. If we find a conflict, we backtrack and try a different assignment.

#Notes:

#If both literals are false, then we have a conflict.


from typing import Any


def clause_satisfied(clause, assignment):
    return any(
        (literal > 0 and assignment.get(abs(literal)) is True)
        or (literal < 0 and assignment.get(abs(literal)) is False)
        for literal in clause
    )
def all_clauses_satisfied(clauses, assignment):
    for clause in clauses: 
        if not clause_satisfied(clause, assignment):
            return False
    return True



def check_falsified(literal, assignment):
    val = assignment.get(abs(literal))
    if val is None:
        return False
    if literal > 0:
        return val is False
    return val is True


def precompute_watched_literals(clauses):
    return [list(clause[:2]) for clause in clauses]

def update_single_watched(new_assignment, watched):
    # IF there is a single watched literal, we update the assignment to satisfy that literal.
    var = abs(watched[0])
    want_true = watched[0] > 0
    cur = new_assignment.get(var)
    if cur is None:
        new_assignment[var] = want_true
        return new_assignment, True
    if cur is not want_true:
        return None, False
    return new_assignment, False


def update_double_watched(new_assignment, clause, watched):
    # If there are two watched literals, we check if either of them is false. If one is false, we look for another literal to watch.
    changed = False
    if check_falsified(watched[0], new_assignment):
        new_assignment, did_replace = check_literals(clause, new_assignment, watched, 0)
        if did_replace:
            changed = True
        else:
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
            new_assignment, did_unit = update_single_watched(new_assignment, [watched[0]])
            if new_assignment is None:
                return None, False
            if did_unit:
                changed = True
    return new_assignment, changed


def check_literals(clause, assignment, watched, idx_replace):
    other_lit = watched[1 - idx_replace]
    for literal in clause:
        if literal == other_lit:
            continue
        if not check_falsified(literal, assignment):
            watched[idx_replace] = literal
            return assignment, True
    return assignment, False


#Updates Assignment based on watched literals.
def watched_bcp(clauses, assignment: dict, watched_list: list):
    new_assignment = assignment.copy()
    changed = True
    while changed:
        changed = False
        for i, clause in enumerate(clauses):
            watched = watched_list[i]
            if len(watched) == 0:
                if clause_satisfied(clause, new_assignment):
                    continue
                return None
            elif len(watched) == 1:
                new_assignment, did_unit = update_single_watched(new_assignment, watched)
                if new_assignment is None:
                    return None
                if did_unit:
                    changed = True
            else:
                new_assignment, did_double = update_double_watched(new_assignment, clause, watched)
                if new_assignment is None:
                    return None
                if did_double:
                    changed = True
    return new_assignment
