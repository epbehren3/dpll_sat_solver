import time 
import tracemalloc
import os 

# Default when METRICS_LOG_FILE is unset (e.g. `python main.py f.cnf`).
logpath = "logs/metrics_200_860.txt"


def _metrics_output_path() -> str:
    return os.environ.get("METRICS_LOG_FILE", logpath)


class simpleMetrics(): 
    #Class to grab simple metrics and store them in a log file.
    def __init__(self): 
        self.wall_time     = 0.0   # real elapsed time
        self.cpu_time      = 0.0   # actual CPU time used
        self.peak_mem_kb   = 0.0 
        self.result        = None

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
        # Use 'a' mode to append metrics to the log file.
        out = _metrics_output_path()
        parent = os.path.dirname(out)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(out, "a") as f:
            f.write(f"Wall Time: {self.wall_time}\n")
            f.write(f"CPU Time: {self.cpu_time}\n")
            f.write(f"Peak Memory: {self.peak_mem_kb} KB\n")
            f.write(f"Result: {self.result}\n")

