#!/usr/bin/env bash
# Run main.py (DPLL + chaff + DLIS) on every .cnf under SATLIB benchmark dirs.
# Runs are strictly sequential (one CNF at a time). Each run writes one metrics file.
#
# Usage:
#   ./run_all_satlib.sh                      # all top-level satlib_* directories (recursive)
#   ./run_all_satlib.sh satlib_20_91         # one directory only (recursive)
#
# Environment:
#   SATLIB_LOG_ROOT   Base directory for per-run logs (default: logs/satlib_batch)
#   SATLIB_EXPECT     If set to "sat" or "unsat", use that as the expected label for
#                     *every* benchmark directory when computing accuracy.
#                     If unset, expectation is inferred from the directory name:
#                     basename ends with _sat -> SAT; contains "unsat" -> UNSAT; else n/a.
#
# Metrics: METRICS_LOG_FILE is set per run (see grabMetrics.py).

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
  for d in satlib_*/; do
    [[ -d "$d" ]] && DIRS+=("${d%/}")
  done
  shopt -u nullglob
  if [[ ${#DIRS[@]} -eq 0 ]]; then
    echo "No satlib_* directories found in $SCRIPT_DIR (pass one explicitly: $0 satlib_20_91)" >&2
    exit 1
  fi
fi

mkdir -p "$LOG_ROOT"

total=0
for d in "${DIRS[@]}"; do
  d_base="$(basename "$d")"
  echo "========== $d ($d_base) =========="
  mkdir -p "$LOG_ROOT/$d_base"

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
    rel="${f#${d}/}"
    safe_rel="${rel//\//__}"
    mlog="$LOG_ROOT/$d_base/${safe_rel}.metrics.txt"

    echo "=== ($total) $f -> $mlog ==="
    {
      printf '# CNF: %s\n' "$f"
    } >"$mlog"
    export METRICS_LOG_FILE="$mlog"
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

  SATLIB_EXPECT_DIR="$exp" "$PY" - "$LOG_ROOT" "$d_base" <<'PY'
import glob
import os
import sys

root, dbase = sys.argv[1], sys.argv[2]
exp = (os.environ.get("SATLIB_EXPECT_DIR") or "").strip().lower()
path = os.path.join(root, dbase)
files = sorted(glob.glob(os.path.join(path, "*.metrics.txt")))
if not files:
    print(f"\n{dbase}: (no .metrics.txt files in {path})")
    sys.exit(0)

walls = []
results = []
for fp in files:
    w = r = None
    with open(fp, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("Wall Time:"):
                w = float(line.split()[2])
            elif line.startswith("Result:"):
                r = line.split()[1].strip()
    if w is not None:
        walls.append(w)
    if r is not None:
        results.append(r)

n = len(walls)
avg_wall = sum(walls) / n if n else 0.0
sat_n = sum(1 for x in results if x == "SAT")
uns_n = sum(1 for x in results if x == "UNSAT")
m = len(results)

print(f"\n{dbase}:")
print(f"  runs (metrics files): {len(files)}")
print(f"  parsed wall samples:  {n}")
print(f"  average wall time (s): {avg_wall:.6f}" if n else "  average wall time (s): n/a")
print(f"  verdicts: SAT={sat_n}, UNSAT={uns_n} (parsed {m})")

if exp in ("sat", "unsat"):
    expect_sat = exp == "sat"
    ok = 0
    for x in results:
        if expect_sat and x == "SAT":
            ok += 1
        if (not expect_sat) and x == "UNSAT":
            ok += 1
    pct = (100.0 * ok / m) if m else 0.0
    print(f"  expected ({exp.upper()}, from dir/env): {ok}/{m} correct ({pct:.2f}% accuracy)")
else:
    print("  accuracy: n/a (no expected SAT/UNSAT label; dirname does not end with _sat / unsat, and SATLIB_EXPECT unset)")
PY
done

echo ""
echo "Done. Ran main.py on $total .cnf file(s)."
