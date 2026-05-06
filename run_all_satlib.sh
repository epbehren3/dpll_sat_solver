#!/usr/bin/env bash
# Run main.py (DPLL + chaff + DLIS) on every .cnf under SATLIB benchmark dirs.
# All results for a benchmark dir are appended to one shared metrics file.
# A master summary sheet is written to $LOG_ROOT/satlib_sheet.csv.
#
# Usage:
#   ./run_all_satlib.sh                      # all top-level satlib_* directories (recursive)
#   ./run_all_satlib.sh satlib_20_91         # one directory only (recursive)
#
# Environment:
#   SATLIB_LOG_ROOT   Base directory for logs (default: logs/satlib_batch)
#   SATLIB_EXPECT     If set to "sat" or "unsat", use that as the expected label for
#                     *every* benchmark directory when computing accuracy.
#                     If unset, expectation is inferred from the directory name:
#                     basename ends with _sat -> SAT; contains "unsat" -> UNSAT; else n/a.
#
# Output files:
#   $LOG_ROOT/<benchmark>.metrics.txt   one shared file per benchmark dir (appended per run)
#   $LOG_ROOT/satlib_sheet.csv          master summary sheet across all dirs

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

LOG_ROOT="${SATLIB_LOG_ROOT:-logs/satlib_batch}"
export LOG_ROOT

DIRS=()
if [[ $# -ge 1 ]]; then
  if [[ ! -d "$1" ]]; then
    echo "Not a directory: $1" >&2
    exit 1
  fi
  DIRS=("$1")
else
  shopt -s nullglob
  tmp_dirs=()
  for d in satlib_*/; do
    [[ -d "$d" ]] && tmp_dirs+=("${d%/}")
  done
  shopt -u nullglob
  if [[ ${#tmp_dirs[@]} -eq 0 ]]; then
    echo "No satlib_* directories found in $SCRIPT_DIR (pass one explicitly: $0 satlib_20_91)" >&2
    exit 1
  fi
  # Sort numerically by the variable count (second field after splitting on '_')
  while IFS= read -r d; do
    DIRS+=("$d")
  done < <(printf '%s\n' "${tmp_dirs[@]}" | sort -t_ -k2 -n)
fi

mkdir -p "$LOG_ROOT"

total=0
for d in "${DIRS[@]}"; do
  d_base="$(basename "$d")"
  echo "========== $d ($d_base) =========="

  # One shared metrics file per benchmark directory
  METRICS_LOG_FILE="$LOG_ROOT/${d_base}.metrics.txt"
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
    if ! "$PY" main.py "$f"; then
      echo "(non-zero exit: $f)" >&2
    fi
  done
done

echo ""
echo "=============================="
echo "Summary (per benchmark directory)"
echo "Log root: $LOG_ROOT"
echo "=============================="

SHEET="$LOG_ROOT/satlib_sheet.csv"
printf 'Benchmark,CNFs,SAT,UNSAT,Incomplete,Accuracy%%,AvgWall(s),MinWall(s),MaxWall(s),TotalWall(s)\n' > "$SHEET"

for d in "${DIRS[@]}"; do
  d_base="$(basename "$d")"
  exp=""
  if [[ -n "${SATLIB_EXPECT:-}" ]]; then
    exp="$(printf '%s' "${SATLIB_EXPECT}" | tr '[:upper:]' '[:lower:]')"
  else
    case "$d_base" in
      *_sat) exp="sat" ;;
      *unsat* | *UNSAT*) exp="unsat" ;;
      *) exp="" ;;
    esac
  fi

  SATLIB_EXPECT_DIR="$exp" "$PY" - "$LOG_ROOT" "$d_base" "$SHEET" <<'PY'
import os
import sys

root, dbase, sheet_path = sys.argv[1], sys.argv[2], sys.argv[3]
exp = (os.environ.get("SATLIB_EXPECT_DIR") or "").strip().lower()
metrics_file = os.path.join(root, f"{dbase}.metrics.txt")

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
echo "Done. Ran main.py on $total .cnf file(s)."
