# main.py - Solver entry point
# ECE 51216 - Spring 2026 - Behrendt & Morshed
#
# Parses a DIMACS CNF file, runs DPLL, and prints True/False (SAT/UNSAT).
#
# Usage:
#   python3 main.py <path/to/instance.cnf>

import sys
from dimacs import dimacs
from dpll import dpll
from chaff import precompute_watched_literals


def main(argv=None):
    argv = argv if argv is not None else sys.argv
    path = argv[1]

    # Parse the DIMACS CNF file into a list of clauses
    num_var, clauses = dimacs(path)

    # Initialise every variable as unassigned (None)
    assignment = {i + 1: None for i in range(num_var)}

    # Pre-compute watched literals so dpll() reuses them across calls
    watched_list = precompute_watched_literals(clauses)

    result = False
    #Try DPLL Algorithm
    
    try:
        result = dpll(clauses, assignment, watched_list)
    except Exception as e:
        print(e)
        result = False

    print("RESULT:SAT") if result else print("RESULT:UNSAT")

    if result:
        assignment_str = " ".join(
            f"{var}={1 if assignment[var] else 0}"
            for var in sorted(assignment)
        )
        print(f"ASSIGNMENT:{assignment_str}")


if __name__ == "__main__":
    main()
