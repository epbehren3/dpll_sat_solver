#!/usr/bin/env bash
# Run main.py on every .cnf under satlib/ (recursive).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

mapfile -t files < <(find satlib_200_860 -type f -name '*.cnf' | sort)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No .cnf files found under satlib_200_860/" >&2
  exit 1
fi

for f in "${files[@]}"; do
  echo "=== ${f} ==="
  "$PY" main.py "$f" || echo "(failed: exit $?)" >&2
done
