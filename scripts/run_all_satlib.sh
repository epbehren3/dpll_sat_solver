#!/usr/bin/env bash
# Run src/main.py on SATLIB CNFs and append per-directory metrics.
#
# Usage:
#   ./run_all_satlib.sh
#     -> run all immediate benchmark directories inside:
#          <repo>/benchmarks/SAT and <repo>/benchmarks/UNSAT
#
#   ./run_all_satlib.sh <dir>
#     -> if <dir> basename is SAT or UNSAT, run all immediate subdirectories
#     -> otherwise run only <dir> recursively
#
# Environment:
#   SATLIB_LOG_ROOT   Base directory for logs
#                     (default: <repo>/test_results/satlib_batch)
#   SATLIB_EXPECT     Force expected label ("sat" or "unsat") for every benchmark
#
# Output files:
#   $LOG_ROOT/<benchmark>_basic.metrics.txt   one shared file per benchmark dir
#   $LOG_ROOT/satlib_sheet_basic.csv          summary sheet across all dirs

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MAIN_PY="$REPO_ROOT/src/main.py"

if [[ ! -f "$MAIN_PY" ]]; then
  echo "Could not find solver entrypoint at $MAIN_PY" >&2
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

LOG_ROOT="${SATLIB_LOG_ROOT:-$REPO_ROOT/test_results/satlib_batch}"
export LOG_ROOT

gather_child_dirs() {
  local parent="$1"
  local child
  shopt -s nullglob
  for child in "$parent"/*; do
    [[ -d "$child" ]] || continue
    printf '%s\n' "$child"
  done | sort
  shopt -u nullglob
}

DIRS=()
if [[ $# -ge 1 ]]; then
  arg="$1"
  if [[ ! -d "$arg" ]]; then
    echo "Not a directory: $arg" >&2
    exit 1
  fi
  arg_abs="$(cd "$arg" && pwd)"
  arg_base="$(basename "$arg_abs")"
  arg_upper="$(printf '%s' "$arg_base" | tr '[:lower:]' '[:upper:]')"

  if [[ "$arg_upper" == "SAT" || "$arg_upper" == "UNSAT" ]]; then
    while IFS= read -r d; do
      DIRS+=("$d")
    done < <(gather_child_dirs "$arg_abs")
  else
    DIRS=("$arg_abs")
  fi
else
  for root_dir in "$REPO_ROOT/benchmarks/SAT" "$REPO_ROOT/benchmarks/UNSAT"; do
    [[ -d "$root_dir" ]] || continue
    while IFS= read -r d; do
      DIRS+=("$d")
    done < <(gather_child_dirs "$root_dir")
  done
fi

if [[ ${#DIRS[@]} -eq 0 ]]; then
  echo "No benchmark directories found. Provide a SAT/UNSAT folder or a benchmark directory path." >&2
  exit 1
fi

mkdir -p "$LOG_ROOT"

total=0
for d in "${DIRS[@]}"; do
  d_base="$(basename "$d")"
  echo "========== $d ($d_base) =========="

  METRICS_LOG_FILE="$LOG_ROOT/${d_base}_basic.metrics.txt"
  export METRICS_LOG_FILE

  files=()
  while IFS= read -r f; do
    files+=("$f")
  done < <(find "$d" -type f -name '*.cnf' | sort)

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "No .cnf files under $d" >&2
    continue
  fi

  for f in "${files[@]}"; do
    total=$((total + 1))
    echo "=== ($total) $f ==="
    printf '# CNF: %s\n' "$f" >> "$METRICS_LOG_FILE"
    if ! "$PY" "$MAIN_PY" "$f"; then
      echo "(non-zero exit: $f)" >&2
    fi
  done
done

echo ""
echo "=============================="
echo "Summary (per benchmark directory)"
echo "Log root: $LOG_ROOT"
echo "=============================="

SHEET="$LOG_ROOT/satlib_sheet_basic.csv"
printf 'Benchmark,CNFs,SAT,UNSAT,Incomplete,Accuracy%%,AvgWall(s),MinWall(s),MaxWall(s),TotalWall(s)\n' > "$SHEET"

for d in "${DIRS[@]}"; do
  d_base="$(basename "$d")"
  exp=""
  if [[ -n "${SATLIB_EXPECT:-}" ]]; then
    exp="$(printf '%s' "${SATLIB_EXPECT}" | tr '[:upper:]' '[:lower:]')"
  else
    d_lower="$(printf '%s' "$d" | tr '[:upper:]' '[:lower:]')"
    case "$d_lower" in
      */sat/*) exp="sat" ;;
      */unsat/*) exp="unsat" ;;
      *)
        case "$d_base" in
          *_sat) exp="sat" ;;
          *unsat* | *UNSAT*) exp="unsat" ;;
          *) exp="" ;;
        esac
        ;;
    esac
  fi

  SATLIB_EXPECT_DIR="$exp" "$PY" - "$LOG_ROOT" "$d_base" "$SHEET" <<'PY'
import os
import sys

root, dbase, sheet_path = sys.argv[1], sys.argv[2], sys.argv[3]
exp = (os.environ.get("SATLIB_EXPECT_DIR") or "").strip().lower()
metrics_file = os.path.join(root, f"{dbase}_basic.metrics.txt")

if not os.path.exists(metrics_file):
    print(f"\n{dbase}: (no metrics file at {metrics_file})")
    sys.exit(0)

# Parse all runs from the shared file; each run is delimited by a "# CNF:" header.
runs = 0
walls = []
results = []
cur_wall = cur_result = None

with open(metrics_file, encoding="utf-8", errors="replace") as f:
    for line in f:
        if line.startswith("# CNF:"):
            if runs > 0:
                if cur_wall   is not None: walls.append(cur_wall)
                if cur_result is not None: results.append(cur_result)
            runs += 1
            cur_wall = cur_result = None
        elif line.startswith("Wall Time:"):
            try: cur_wall = float(line.split()[2])
            except: pass
        elif line.startswith("Result:"):
            cur_result = line.split()[1].strip()
    # flush last entry
    if cur_wall   is not None: walls.append(cur_wall)
    if cur_result is not None: results.append(cur_result)

n        = len(walls)
avg_wall = sum(walls) / n if n else 0.0
sat_n    = sum(1 for x in results if x == "SAT")
uns_n    = sum(1 for x in results if x == "UNSAT")
incomplete = runs - len(results)

print(f"\n{dbase}:")
print(f"  runs:                {runs}")
print(f"  average wall time (s): {avg_wall:.6f}" if n else "  average wall time (s): n/a")
print(f"  verdicts: SAT={sat_n}, UNSAT={uns_n}, incomplete={incomplete}")

acc_str = "n/a"
if exp in ("sat", "unsat"):
    expect_sat = exp == "sat"
    ok  = sum(1 for x in results if (expect_sat and x == "SAT") or (not expect_sat and x == "UNSAT"))
    m   = len(results)
    pct = (100.0 * ok / m) if m else 0.0
    acc_str = f"{pct:.2f}"
    print(f"  expected ({exp.upper()}): {ok}/{m} correct ({pct:.2f}% accuracy)")
else:
    print("  accuracy: n/a (dirname does not end with _sat / unsat, and SATLIB_EXPECT unset)")

# Append one row to the master CSV sheet
min_w = f"{min(walls):.6f}" if walls else "n/a"
max_w = f"{max(walls):.6f}" if walls else "n/a"
tot_w = f"{sum(walls):.6f}" if walls else "n/a"
avg_w = f"{avg_wall:.6f}"   if walls else "n/a"
with open(sheet_path, "a", encoding="utf-8") as sf:
    sf.write(f"{dbase},{runs},{sat_n},{uns_n},{incomplete},{acc_str},{avg_w},{min_w},{max_w},{tot_w}\n")
PY
done

echo ""
echo "Master sheet: $SHEET"
echo "Done. Ran src/main.py on $total .cnf file(s)."
