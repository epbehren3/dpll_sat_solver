#Watched literals

#IF watched literals are not false, then the clause is satisfied and not a unit clause

# If one of the two literals is false, then we look for another literal in the clause that is not false to watch instead.

#If we find one, we update the watched literals and continue. If we cannot find a new literal to watch,

# then the clause becomes a unit clause, and we can infer the value of the remaining unassigned literal.

#Once we determine there is only one unassigned literal left in the clause. We infer a value that satisfied the literal

# and run BCP to propagate the consequences of this assignment. If we find a conflict, we backtrack and try a different assignment.

#Notes:

#If both literals are false, then we have a conflict.


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


#Function updates watched literals.
def watched_literals(clause, assignment):
    #Literally just iterates through the clause to determine if a literal has not been assigned yet.
    watched = []
    for literal in clause:
        var = abs(literal)
        if (literal > 0 and assignment.get(var) is True) or (literal < 0 and assignment.get(var) is False):
            #If the literal is satisfied, we can stop watching this clause.
                break
    return watched

def precompute_watched_literals(clauses, assignment):
    #Watched literals key to match clause length
    watched_literals = []
    master_list = []
    for clause in clauses: 
        if(idx, literal in enumerate(clause) and assignment.get(abs(literal)) is None and literal not in watched_literals[len(clause)] and len(watched_literals) < 2):
            watched_literals[idx].append(literal)
        master_list.append(watched_literals)

    return master_list

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
    if check_falsified(watched[0], new_assignment) and check_falsified(watched[1], new_assignment):
        #If both watched literals are false, we have a conflict. Backtrack.
        return None, False
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

        if literal is other_lit:
def check_literals(clause, assignment, watched, idx_replace):
    new_assignment = assignment.copy()
    other_lit = watched[1 - idx_replace]
    for literal in clause:
        if literal is other_lit:
            continue
        if not check_falsified(literal, new_assignment):
            watched[idx_replace] = literal
            return new_assignment, True
    return new_assignment, False


#Updates Assignment based on watched literals.
def watched_bcp(clauses, assignment: dict):
    new_assignment = assignment.copy()
    #Loop through continuously until there are no more changes to the assignment.
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            #Call watched literals to detrmine assignment update.
            watched = watched_literals(clause, new_assignment)
            if len(watched) == 0:
                #If there are no watched literals, the clause has been satisfied.
                #This was a correctness check that my LLM suggested when I was learning about watched literals, I am unsure if this logic makes sense or is necessary.
                if clause_satisfied(clause, new_assignment):
                    continue
                #If the clause is not satisfied, we have a conflict. Backtrack.
                return None
            if len(watched) == 1:
                new_assignment, did_unit = update_single_watched(new_assignment, watched)
                if new_assignment is None:
                    return None
                if did_unit:
                    changed = True
            if len(watched) == 2:
                new_assignment, did_double = update_double_watched(new_assignment, clause, watched)
                if new_assignment is None:
                    return None
                if did_double:
                    changed = True
    return new_assignment
