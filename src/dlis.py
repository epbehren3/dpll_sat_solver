#DLIS Decision Heuristic Implementation
#Consists of (2) functions, the first one, clauseSat()) is used to check if a clause has been satisifed or not based on the variable assignments
#Next, in the dlis() function, we will check unsat clauses and decide on a literal to return based on the literal that appears the most.

#Create a function to check if the clause has been satisfied or not based on the variable assignments
def clauseSat(clause, assignment):
    #To check if the clause is satisfied, we need to check each literal 
    for literal in clause:

        #Take the absolute value of the literal to get the variable, because that's how we'll be able to check if it's been assigned
        var = abs(literal)

        #Only check variables which have been assigned
        if var in assignment:
            #If the literal was assigned as true, we return sat as True
            if literal > 0:
                value = assignment[var]

            #If the literal was negative, we return sat as the complement of the literal 
            else:
                value = not assignment[var] 

            #If it's been assigned as true, we want to return that the clause is satisfied
            if value is True:
                return True
                          
    return False
                    

def dlis(clauses, assignment):
    #Define a variable to keep count of each literal
    counts = {} 
    highestCount = -1
    #For each clause in the list of clauses, we want to check if it's satisfied
    for clause in clauses:
        clause_sat = clauseSat(clause, assignment)

        if not clause_sat:
            #Meaning that the clause is not satisfied, so we want to now count the literals 
            for literal in clause:
                var = abs(literal)

                # Count literals whose variable is still unassigned (missing or None).
                if assignment.get(var) is None:

                    if literal in counts:
                        counts[literal] +=1
                    else:
                        counts[literal] = 1
    
    #Check to see which literal is actually the best to return, based on which one appeared the most
    for literal in counts:
        if counts[literal] > highestCount:
            highestCount = counts[literal]
            decidedLiteral = literal
            
    if not counts:
        return None
    
    return decidedLiteral





#note: used LLM to create test cases to test the DLIS
#test case
#def main():
#    clauses = [[-2,1,3,4,5,1,-7,-7,-7,-7], [-7,-7,2, 3]]
#    assignment = {1: True}
#    result = dlis(clauses, assignment)
#    print(result)

#main()