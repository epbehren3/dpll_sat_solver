#open the file, skip comment lines, parse the problem line
#problem line will look like p cnf <num_vars> <num_clauses>
#https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html

#sample text file:
#p cnf 3 2 
#1 -3 8 0 (clause 1, ending w/ a trailing 0)
#2 3 -1 0 (clause 2, ending w/ a trailing 0)
#this tells us that the cnf is (x1 + x3') and (x2 + x3 + x1')

def dimacInput(path):
    numLiterals = numClauses = 0
    clauses = []
    with open(path) as fo: 
        for line in fo:
            line = line.strip()
            #ignore if it's a new/empty line
            if not line: 
                continue
            #ignore the comment lines
            if line.startswith('c'): 
                continue
            #if it starts with p, yesssssssssss
            if line.startswith('p'):

                #splitting at the white space between numLiterals and numClauses
                parts = line.split() 
                numLiterals = int(parts[2]) 
                numClauses = int(parts[3]) 
                continue

            parts = list(map(int, line.split()))
            #remove the trailing 0 at the end of the clause
            parts.pop()
            clauses.append(parts)

    #function returns the number of literals in the cnf formula
    #and the clauses in the function as a list
    return numLiterals, clauses

# def main():
#     numLiterals, clauses = dimacInput("test.txt")
#     print(numLiterals)
#     print(clauses)

# if __name__ == "__main__":
#     main()
