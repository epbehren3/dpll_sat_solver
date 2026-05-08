# dimacs.py - DIMACS CNF file parser


def dimacs(path):
    num_var = num_clauses = 0
    clauses = []

    with open(path) as fo:
        for line in fo:
            line = line.strip()

            # Skip comment lines and blank lines
            if line.startswith('c') or not line:
                continue

            # SATLIB files end with '%' — stop reading
            if '%' in line:
                break

            # Problem header: "p cnf <num_vars> <num_clauses>"
            if line.startswith('p'):
                parts = line.split()
                num_var = int(parts[2])
                num_clauses = int(parts[3])
                continue

            # Clause line: space-separated literals terminated by 0
            parts = list(map(int, line.split()))
            parts.pop()  # remove trailing 0 delimiter

            # Skip empty clauses that arise after stripping the 0
            if not parts:
                continue

            clauses.append(parts)

    return num_var, clauses
