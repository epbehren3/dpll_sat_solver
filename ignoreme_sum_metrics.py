#!/usr/bin/env python3

import re
import sys

def sum_metrics(filename):
    wall_times = []
    cpu_times = []
    peak_memories = []
    sat_count = 0
    unsat_count = 0

    with open(filename, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        if lines[i].startswith('Wall Time:'):
            wall_time = float(re.search(r'Wall Time: ([\d.]+)', lines[i]).group(1))
            wall_times.append(wall_time)
        elif lines[i].startswith('CPU Time:'):
            cpu_time = float(re.search(r'CPU Time: ([\d.]+)', lines[i]).group(1))
            cpu_times.append(cpu_time)
        elif lines[i].startswith('Peak Memory:'):
            peak_memory = float(re.search(r'Peak Memory: ([\d.]+)', lines[i]).group(1))
            peak_memories.append(peak_memory)
        elif lines[i].startswith('Result:'):
            if lines[i].strip() == 'Result: SAT':
                sat_count += 1
            elif lines[i].strip() == 'Result: UNSAT':
                unsat_count += 1
        i += 1

    total_wall = sum(wall_times)
    total_cpu = sum(cpu_times)
    total_peak = sum(peak_memories)

    print(f"Total Wall Time: {total_wall}")
    print(f"Total CPU Time: {total_cpu}")
    print(f"Total Peak Memory: {total_peak} KB")
    print(f"SAT count: {sat_count}")
    print(f"UNSAT count: {unsat_count}")

    # Min / Max / Avg
if wall_times:
    print(f"Min Wall Time: {min(wall_times)}")
    print(f"Max Wall Time: {max(wall_times)}")
    print(f"Avg Wall Time: {total_wall / len(wall_times)}")

if cpu_times:
    print(f"Min CPU Time: {min(cpu_times)}")
    print(f"Max CPU Time: {max(cpu_times)}")
    print(f"Avg CPU Time: {total_cpu / len(cpu_times)}")

if peak_memories:
    print(f"Min Peak Memory: {min(peak_memories)} KB")
    print(f"Max Peak Memory: {max(peak_memories)} KB")
    print(f"Avg Peak Memory: {total_peak / len(peak_memories)} KB")

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'logs/metrics_20_91.txt'
    sum_metrics(filename)
