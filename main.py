import grabMetrics
from dimacs import dimacs
from dpll import dpll

path  = ""
#path = "test_cases/aim-100-6_0-yes1-1.cnf"

def main(): 
    
    #Grab Dimacs
    num_var, clauses = dimacs(path)
    #print(num_var)
    #Set inital assingments
    assignment = {i+1: False for i in range(num_var)}
    #Simply run the DPLL
    result = dpll(clauses, assignment, grabMetrics)

if __name__ == "__main__":
    main()