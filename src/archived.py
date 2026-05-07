


#Archived Heuristics to be phased out for decision heuristics. 


#Replace with Watched BCP
# Simple BCP implementation.
# Returns a propagated assignment dict, or None on conflict.
def bcp(clauses, assignment):
    new_assignment = assignment.copy()

    changed = True
    while changed:
        changed = False
        for clause in clauses:
            satisfied = False
            unassigned = []

            for literal in clause:
                val = new_assignment.get(abs(literal))
                if val is None:
                    unassigned.append(literal)
                elif (literal > 0 and val is True) or (literal < 0 and val is False):
                    satisfied = True
                    break

            if satisfied:
                continue

            # Clause is fully falsified under current assignment.
            if len(unassigned) == 0:
                return None

            # Unit clause: force the last remaining literal.
            if len(unassigned) == 1:
                unit_literal = unassigned[0]
                var = abs(unit_literal)
                should_be_true = unit_literal > 0
                current_value = new_assignment.get(var)

                if current_value is None:
                    new_assignment[var] = should_be_true
                    changed = True
                elif current_value is not should_be_true:
                    return None
             

    return new_assignment

def force_assign(literal, Assignment):
    Assignment[abs(literal)] = (literal > 0)
    return Assignment[abs(literal)]


#Simple Replacement for DPLL.
def first_unassigned(clauses, assignment):
    for clause in clauses:
        for literal in clause:
            if assignment.get(abs(literal)) is None:
                return literal
    return None
