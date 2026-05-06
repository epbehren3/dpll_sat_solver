from grabMetrics import simpleMetrics
import sys
from dimacs import dimacs
from dpll import dpll
from chaff import precompute_watched_literals
metrics = simpleMetrics()
#Test to check webhook

def main(argv=None):
    argv = argv if argv is not None else sys.argv
    path = argv[1]
    num_var, clauses = dimacs(path)
    # Unassigned variables must be None for watched_literals / DLIS.
    assignment = {i + 1: None for i in range(num_var)}
    result = False
    metrics.start()
    watched_list = precompute_watched_literals(clauses)
    try:
        result = dpll(clauses, assignment, watched_list)
    except Exception as e:
        print(e)
        result = False
    finally:
        metrics.stop(result)
    print(result)

    metrics.report()

if __name__ == "__main__":
    main()



    