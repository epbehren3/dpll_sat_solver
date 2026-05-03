#!/usr/bin/env python3

from pathlib import Path
import argparse


def find_satlib_cnf_files(root):
    cnf_files = []

    for path in root.iterdir():
        if path.is_dir() and path.name.startswith("satlib"):
            cnf_files.extend(path.rglob("*.cnf"))

    return sorted(cnf_files)


def clean_satlib_cnf_bytes(data):
    """Drop a SATLIB-style line that is only %%, plus a lone 0 on the next line; then strip remaining %% bytes."""
    lines = data.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        core = lines[i].rstrip(b"\r\n").strip()
        if core == b"%":
            i += 1
            if i < len(lines) and lines[i].rstrip(b"\r\n").strip() == b"0":
                i += 1
            continue
        out.append(lines[i])
        i += 1
    data = b"".join(out)
    return data.replace(b"%", b"")


def process_cnf_file(path, dry_run=False):
    """Rewrite the file if SATLIB %%/footer cleanup changes bytes. Returns True if a write would occur."""
    data = path.read_bytes()
    new_data = clean_satlib_cnf_bytes(data)
    if new_data == data:
        return False
    if not dry_run:
        path.write_bytes(new_data)
    return True


def main():
    parser = argparse.ArgumentParser(
        description=(
            "SATLIB CNF cleanup under satlib* dirs: remove a line that is only %%, "
            "remove the following line if it is only 0, then remove every remaining %% byte."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to search from. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would change without modifying them.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cnf_files = find_satlib_cnf_files(root)

    if not cnf_files:
        print(f"No .cnf files found in satlib directories under {root}")
        return

    changed = 0
    for cnf_file in cnf_files:
        if process_cnf_file(cnf_file, dry_run=args.dry_run):
            changed += 1
            verb = "Would clean" if args.dry_run else "Cleaned"
            print(f"{verb} {cnf_file}")

    print(f"{'Would modify' if args.dry_run else 'Modified'} {changed} of {len(cnf_files)} .cnf file(s).")


if __name__ == "__main__":
    main()
