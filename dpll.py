#Basic DPLL Implementation, first assigns values to variables using watched literals, and then calls DLIS if 
# There are still unsatisfied clauses to decide on a literal to branch on.
#The main function is dpll(), which takes in a list of clauses and an assignment of variables, and returns True if the formula is satisfiable, and False otherwise.

#Main flow works like this 
# 1. Run Watched BCP to check the consequences of our current assignment. If we find a conflict, we backtrack and try a different assignment.
#  
import chaff 
import dlis
import grabMetrics


def dpll(clauses, assignment,metrics: grabMetrics):
    
    
    #First we run BCP to propagate the consequences of our current assignment. 
    new_assignment = chaff.watched_bcp(clauses, assignment)

    if new_assignment is None:
        #If conflict, backtrack  
        return False

    #Look for conflicts
    if all(chaff.watched_literals(clause, new_assignment) == [] for clause in clauses):
        return True

    #IF there are still unsatisfied clauses we need to call DLIS to pick a literal. 
    literal = dlis.dlis(clauses, new_assignment)

    if literal is None:
        #If there are no unassigned literals left, but not all clauses are satisfied, we have a conflict. Backtrack. 
        return False

#DFS Logic,  We branch on the chosen literal and go several layers deep. Once we reach a fail, we go back and try the other node. 
    #Branch on the chosen literal being true.
    new_assignment[literal] = True
    if dpll(clauses, new_assignment, metrics):
        return True

    #Branch on the chosen literal being false.
    new_assignment[literal] = False
    if dpll(clauses, new_assignment, metrics):
        return True

    #If neither branch leads to a solution, we backtrack.
    return False





