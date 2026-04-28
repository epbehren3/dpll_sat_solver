import time 
import tracemalloc
import os 

logpath = "metrics.txt"



class simpleMetrics(): 
    def __init__(self: simpleMetrics): 
        self.wall_time     = 0.0   # real elapsed time
        self.cpu_time      = 0.0   # actual CPU time used
        self.peak_mem_kb   = 0.0  
        self.result        = None

    def start(self: simpleMetrics):
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
        # Use 'a' mode to append metrics to the log file.
        with open(logpath, "a") as f:
            f.write(f"Wall Time: {self.wall_time}\n")
            f.write(f"CPU Time: {self.cpu_time}\n")
            f.write(f"Peak Memory: {self.peak_mem_kb} KB\n")
            f.write(f"Result: {self.result}\n")
