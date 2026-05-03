#!/usr/bin/env bash
# Run main.py (DPLL + chaff + DLIS) on every .cnf under SATLIB benchmark dirs.
#
# Usage:
#   ./run_all_satlib.sh              # all top-level satlib_* directories (recursive)
#   ./run_all_satlib.sh satlib_20_91 # one directory only (recursive)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

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

total=0
for d in "${DIRS[@]}"; do
  echo "========== $d =========="
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
    echo "=== ${f} ==="
    "$PY" main.py "$f" || echo "(failed or non-zero: $f)" >&2
  done
done

echo "Done. Ran main.py on $total .cnf file(s)."
