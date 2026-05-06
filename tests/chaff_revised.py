#Watched literals with stronger Engineering Approach

#Context: 
#Watched literals is a technique used to improve the performance of the DPLL Algorithm and 
#Determine if a function is satisfiable or not.
#The main idea here is to assign boolean outputs to watched literals (Consider Shannon Expansion).

#Instructions:
# 1. For each clause, determine if the watched literals are true. If they are, then the clause is satisfied and not a unit clause.
# 2. If the literal is considered Unknown, we simply leave it to continue being watched. 
#If the literal is considered False, then we want to relace the watched literal with a new literal that is unknown. 
#If either of the boolean literals is true, then we can ignore the clause and keep moving. 
#If none of them are true then we have a conflict and we need to backtrack. 




def literal_status(literal, assignment):
    # Returns True if literal is satisfied, False if falsified, None if unknown (variable unassigned).
    # This is the only literal-level check you need
    # is_true, is_false, is_unknown all collapse into this
    if literal is None:
        return None
    var = abs(literal)
    val = assignment.get(var)
    if val is None:
        return None
    if literal > 0:
        return val is True
    return val is False


def replace_literal(clause, assignment, watched, id_replace):
    #update the watched literal with a new literal that is unknown. 
    for literal in clause: 
        if literal not in watched and assignment.get(abs(literal)) is None: 
            watched[id_replace] = literal 
            break

    return watched

def is_unit(watched, assignment):
    # One watch is false, other is unknown
    # Triggers forced propagation
    s0 = literal_status(watched[0], assignment)
    s1 = literal_status(watched[1], assignment)
    if s0 is False and s1 is None:
        return True 
    elif s1 is False and s0 is None:
        return True 
    else:
        return False 
    
def is_conflict(watched, assignment):
    # Both watches are false
    # Triggers backtrack
    s0 = literal_status(watched[0], assignment)
    s1 = literal_status(watched[1], assignment)
    if s0 is False and s1 is False:
        return True 
    else:
        return False  

def watched_literals(clause, assignment):
    # The main BCP function
    # Uses literal_status, is_unit, and is_conflict to drive everything
    
    for l in clause:
        if literal_status(l, assignment) is True:
            return []
    unassigned = [l for l in clause if literal_status(l, assignment) is None]
    if not unassigned:
        return []
    watched = [unassigned[0], unassigned[1] if len(unassigned) > 1 else None]
    if watched[1] is not None:
        if literal_status(watched[0], assignment) is False:
            watched = replace_literal(clause, assignment, watched, 0)
        elif literal_status(watched[1], assignment) is False:
            watched = replace_literal(clause, assignment, watched, 1)
    return watched
