 #Watched literals
#IF watched literals are not false, then the clause is satisfied and not a unit clause
# If one of the two literals is false, then we look for another literal in the clause that is not false to watch instead.
#If we find one, we update the watched literals and continue. If we cannot find a new literal to watch, 
# then the clause becomes a unit clause, and we can infer the value of the remaining unassigned literal.
#Once we determine there is only one unassigned literal left in the clause. We infer a value that satisfied the literal
# and run BCP to propagate the consequences of this assignment. If we find a conflict, we backtrack and try a different assignment.
#Notes: 
#If both literals are false, then there is a conflict. 


#Function updates watched literals. 
def watched_literals(clause, assignment):
    #Literally just iterates through the clause to determine if a literal has not been assigned yet,. 
    watched = []
    for literal in clause:
        var =   abs(literal)

        if (literal > 0 and assignment.get(var) is True) or (literal < 0 and assignment.get(var) is False):
            #If the literal is satisfied, we can stop watching this clause. 
            return []
        if assignment.get(var) is None:
            watched.append(literal)
            if len(watched) == 2:
                break
    return watched

#Updates Assignment based on watched literals. 
def watched_bcp(clauses, assignment):
  
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
                if any((literal > 0 and new_assignment.get(abs(literal)) is True) or (literal < 0 and new_assignment.get(abs(literal)) is False) for literal in clause):
                    continue
                else:
                    #If the clause is not satisfied, we have a conflict. Backtrack. 
                    return None
        
            if len(watched) == 1: 
                #IF there is a single watched literal, we update the assignment to satisfy that literal.
                var = abs(watched[0])
                if( watched[0] > 0):
                    new_assignment[var] = True 
                else:
                    new_assignment[var] = False
                changed = True
            if len(watched) == 2:
                #If there are two watched literals, we check if either of them is false. If one is false, we look for another literal to watch. 
                if new_assignment.get(watched[0]) is False and new_assignment.get(watched[1]) is False:
                        #If both watched literals are false, we have a conflict. Backtrack. 
                        return None
                elif new_assignment.get(watched[0]) is False:
                    #If the first literal becomes false we replace. 
                    for literal in clause: 
                        if literal not in watched and new_assignment.get(abs(literal)) is None: 
                            watched[0] = literal 
                            break
                elif new_assignment.get(watched[1]) is False:
                    #If the second literal becomes false we replace. 
                    for literal in clause: 
                        if literal not in watched and new_assignment.get(abs(literal)) is None: 
                            watched[1] = literal 
                            break
            
        #If we have made changes to the assignment, we need to check if there are any new unit clauses that have been created.

    return new_assignment


