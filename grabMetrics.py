import time 
import tracemalloc


logpath = ""



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
        if logpath: 
            f = os.open 