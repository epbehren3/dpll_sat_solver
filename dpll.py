#Basic DPLL Implementation, first assigns values to variables using watched literals, and then calls DLIS if 
# There are still unsatisfied clauses to decide on a literal to branch on.
#The main function is dpll(), which takes in a list of clauses and an assignment of variables, and returns True if the formula is satisfiable, and False otherwise.

#Main flow works like this 
# 1. Run Watched BCP to check the consequences of our current assignment. If we find a conflict, we backtrack and try a different assignment.
#  
import chaff 
import dlis

#Will add more later, for now just need to track metrics.
#import grabMetrics


def dpll(clauses, assignment, watched_list=None):
    if watched_list is None:
        watched_list = chaff.precompute_watched_literals(clauses)

    #First we run BCP to propagate the consequences of our current assignment. 
    new_assignment = chaff.watched_bcp(clauses, assignment, watched_list)

    if new_assignment is None:
        #If conflict, backtrack  
        return False

    #Look for conflicts
    if chaff.all_clauses_satisfied(clauses, new_assignment):
        return True

    #IF there are still unsatisfied clauses we need to call DLIS to pick a literal. 
    literal = dlis.dlis(clauses, new_assignment)

    if literal is None:
        #If there are no unassigned literals left, but not all clauses are satisfied, we have a conflict. Backtrack. 
        return False

    #DFS Logic: branch on the chosen literal, backtrack if both fail.
    var = abs(literal)
    new_assignment[var] = (literal > 0)   # try the polarity DLIS recommended
    if dpll(clauses, new_assignment, [w[:] for w in watched_list]):
        return True

    new_assignment[var] = (literal <= 0)  # try the opposite polarity
    if dpll(clauses, new_assignment, [w[:] for w in watched_list]):
        return True

    return False





