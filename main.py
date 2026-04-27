import time 
import tracemalloc


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


class simpleMetrics(): 
    def __init__: 
        self.wall_time     = 0.0   # real elapsed time
        self.cpu_time      = 0.0   # actual CPU time used
        self.peak_mem_kb   = 0.0
        self.result        = None
        self.backtracks    = 0
        self.clauses_checked = 0
        self.vars_assigned = 0

    def start(self):
        tracemalloc.start()
        self._wall_start = time.perf_counter()
        self._cpu_start  = time.process_time()   # CPU time

    def stop(self, result):
        self.wall_time   = time.perf_counter()  - self._wall_start
        self.cpu_time    = time.process_time()  - self._cpu_start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.peak_mem_kb = peak / 1024
        self.result      = "SAT" if result else "UNSAT"

    def report(self):
        print(f"Result:           {self.result}")
        print(f"Wall Time:        {self.wall_time:.6f} sec")
        print(f"CPU Time:         {self.cpu_time:.6f} sec")  
        print(f"Peak Memory:      {self.peak_mem_kb:.2f} KB")
        print(f"Backtracks:       {self.backtracks}")
        print(f"Clauses Checked:  {self.clauses_checked}")
        print(f"Vars Assigned:    {self.vars_assigned}")
