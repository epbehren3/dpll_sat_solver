import grabMetrics
from dimacs import dimacs
from dpll import dpll

path  = ""
#path = "test_cases/aim-100-6_0-yes1-1.cnf"

metrics = grabMetrics.simpleMetrics()

import sys

def main(): 
    # grab path from command line.
    path = sys.argv[1]
    # Grab Dimacs
    num_var, clauses = dimacs.dimacInput(path)
    # Set initial assignments
    assignment = {i+1: False for i in range(num_var)}
    # Simply run the DPLL
    result = dpll(clauses, assignment, metrics)
    # Print the results
    print(result)
    # Print the metrics
    metrics.report()

if __name__ == "__main__":
    main()