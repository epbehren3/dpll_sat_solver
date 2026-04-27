import grabMetrics

path  = ""




def main(): 
    #Grab Dimacs
    num_var, clauses = dimacs(path)
    #Set iniital assingments
    assignment = {i+1: False for i in range(num_var)}
    #Simply run the DPLL
    result = dpll(clauses, assignment)
    #Print the results
    print(result)

