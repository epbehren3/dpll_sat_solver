#!/usr/bin/env python3

"""Run MiniSat on every .cnf file under a single SatLib directory (recursive)."""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# MiniSat exit codes (classic MiniSat / Homebrew build)
_EXIT_SAT = 10
_EXIT_UNSAT = 20

_CPU_RE = re.compile(r"CPU time\s*:\s*([0-9.eE+-]+)\s*s", re.MULTILINE)


def collect_cnf_files(directory: Path):
    return sorted(directory.rglob("*.cnf"))


def preprocess_cnf_bytes(data: bytes) -> bytes:
    """SATLIB-style cleanup: strip %% bytes, then drop a trailing lone ``0`` line (EOF junk)."""
    data = data.replace(b"%", b"")
    lines = data.splitlines(keepends=True)

    def trimmed(last_line: bytes) -> bytes:
        return last_line.rstrip(b"\r\n").strip()

    while lines:
        t = trimmed(lines[-1])
        if t == b"":
            lines.pop()
        elif t == b"0":
            lines.pop()
        else:
            break

    return b"".join(lines)


def _minisat_argv_rss(minisat_bin: str, tmp: str, result_file: str):
    """If supported, return argv prefixed with /usr/bin/time for peak RSS; else plain minisat argv."""
    time_bin = "/usr/bin/time"
    if not Path(time_bin).is_file():
        return [minisat_bin, tmp, result_file], False
    if sys.platform == "darwin":
        return [time_bin, "-l", minisat_bin, tmp, result_file], True
    if sys.platform.startswith("linux"):
        return [time_bin, "-v", minisat_bin, tmp, result_file], True
    return [minisat_bin, tmp, result_file], False


def _parse_minisat_cpu_s(text: str) -> float | None:
    m = _CPU_RE.search(text or "")
    if not m:
        return None
    return float(m.group(1))


def _parse_rss_bytes_from_time_output(text: str) -> int | None:
    m = re.search(r"^\s*(\d+)\s+peak memory footprint\s*$", text or "", re.MULTILINE)
    if m:
        return int(m.group(1))
    m = re.search(r"^\s*(\d+)\s+maximum resident set size\s*$", text or "", re.MULTILINE)
    if m:
        return int(m.group(1))
    m = re.search(
        r"Maximum resident set size \(kbytes\):\s*(\d+)", text or "", re.IGNORECASE
    )
    if m:
        return int(m.group(1)) * 1024
    m = re.search(r"Maximum resident set size:\s*(\d+)", text or "", re.IGNORECASE)
    if m:
        return int(m.group(1)) * 1024
    return None


def run_with_preprocessed_input(
    minisat_bin,
    cnf: Path,
    result_file: Path,
    *,
    verbose: bool,
    rss: bool,
):
    """Returns (exit_code, captured_stdout_stderr_or_None, cpu_seconds_or_None, rss_bytes_or_None)."""
    raw = cnf.read_bytes()
    cleaned = preprocess_cnf_bytes(raw)

    fd, tmp_name = tempfile.mkstemp(suffix=".cnf", prefix="minisat_")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(cleaned)
        tpath = str(tmp_path)
        rpath = str(result_file)

        wrapped = False
        if rss:
            cmd, wrapped = _minisat_argv_rss(minisat_bin, tpath, rpath)
        else:
            cmd = [minisat_bin, tpath, rpath]

        if verbose:
            proc = subprocess.run(cmd)
            return proc.returncode, None, None, None

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        text = proc.stdout or ""
        cpu_s = _parse_minisat_cpu_s(text)
        rss_bytes = _parse_rss_bytes_from_time_output(text) if (rss and wrapped) else None
        return proc.returncode, text, cpu_s, rss_bytes
    finally:
        tmp_path.unlink(missing_ok=True)


def _format_perf_extra(
    elapsed_ms: float,
    cpu_s: float | None,
    rss_bytes: int | None,
    *,
    show_wall: bool,
    show_cpu: bool,
    show_rss: bool,
) -> str:
    parts = []
    if show_wall:
        parts.append(f"wall={elapsed_ms:.2f}ms")
    if show_cpu and cpu_s is not None:
        parts.append(f"cpu={cpu_s*1000:.3f}ms")
    if show_rss and rss_bytes is not None:
        parts.append(f"rss={rss_bytes/1024/1024:.2f}MiB")
    return f" ({', '.join(parts)})" if parts else ""


def main(argv=None):
    argv = argv if argv is not None else sys.argv
    parser = argparse.ArgumentParser(
        description="Run MiniSat on all .cnf files in one SatLib directory.",
    )
    parser.add_argument(
        "directory",
        help="Path to a satlib directory (e.g. satlib_20_91).",
    )
    parser.add_argument(
        "--minisat",
        default="minisat",
        help="MiniSat executable (default: minisat on PATH).",
    )
    parser.add_argument(
        "--save-results",
        metavar="DIR",
        type=Path,
        default=None,
        help="Write MiniSat result files under DIR (mirrors relative paths); "
        "default discards results to the system null device.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List .cnf files and commands without running MiniSat.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print MiniSat output to the terminal (not captured).",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print the final summary.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Full report: MiniSat log per instance, banners, per-file time (ms), final counts and total time. "
        "Implies verbose MiniSat output; overrides -q.",
    )
    parser.add_argument(
        "--expect",
        choices=("sat", "unsat"),
        default=None,
        help="If set, each SAT/UNSOL result is compared to this label; summary includes match counts and accuracy.",
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Per instance: wall time (always). With captured output (not -v/--all), also parse MiniSat 'CPU time' line.",
    )
    parser.add_argument(
        "--rss",
        action="store_true",
        help="Measure peak RSS via /usr/bin/time (-l on macOS, -v on Linux). Requires captured output; "
        "omit -v/--all for per-line rss=… MiB, or use -v and read 'time' lines at end of each log.",
    )
    args = parser.parse_args(argv[1:])

    if args.all:
        args.quiet = False
    verbose_run = args.verbose or args.all

    _, rss_time_ok = _minisat_argv_rss(args.minisat, "_", "_")
    if args.rss and not rss_time_ok:
        print(
            "Warning: --rss needs /usr/bin/time on macOS or Linux; RSS disabled.",
            file=sys.stderr,
        )
        args.rss = False
    if args.rss and verbose_run:
        print(
            "Note: with -v/--all, RSS is not parsed into each line (output not captured); "
            "run without -v/--all to get rss=… MiB on each line, or read time(1) output under each log.",
            file=sys.stderr,
        )

    root = Path(args.directory).resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1

    cnf_files = collect_cnf_files(root)
    if not cnf_files:
        print(f"No .cnf files under {root}")
        return 0

    if args.save_results is not None:
        args.save_results = args.save_results.resolve()
        args.save_results.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(
            f"Would run MiniSat on {len(cnf_files)} file(s) under {root} "
            "(each CNF: strip %% bytes, drop trailing lone-0 lines, then minisat on a temp file)."
        )
        if args.all:
            print("(With --all: would also print full MiniSat output and timings per file.)")
        if args.expect:
            print(f"(With --expect {args.expect}: would report agreement vs that label.)")
        if args.metrics:
            print("(With --metrics: would report wall time and parsed CPU when output is captured.)")
        if args.rss:
            print("(With --rss: would wrap MiniSat in /usr/bin/time for peak memory where supported.)")

    sat = unsat = other = 0
    matched = mismatched = expect_skipped = 0
    total_t0 = time.perf_counter()
    sum_wall_ms = 0.0
    sum_cpu_s = 0.0
    n_cpu = 0
    max_rss_bytes = 0
    for cnf in cnf_files:
        if args.save_results is not None:
            rel = cnf.relative_to(root)
            result_path = args.save_results / rel.with_suffix(".out")
            result_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            result_path = Path(os.devnull)

        if args.dry_run:
            print(f"# {cnf}")
            print(f"{args.minisat} <preprocessed tmp> {result_path}")
            continue

        if args.all:
            print("=" * 80)
            print(f"instance: {cnf}")
            print("=" * 80)

        t0 = time.perf_counter()
        code, captured, cpu_s, rss_bytes = run_with_preprocessed_input(
            args.minisat,
            cnf,
            result_path,
            verbose=verbose_run,
            rss=args.rss,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        sum_wall_ms += elapsed_ms
        if cpu_s is not None:
            sum_cpu_s += cpu_s
            n_cpu += 1
        if rss_bytes is not None:
            max_rss_bytes = max(max_rss_bytes, rss_bytes)

        if code == _EXIT_SAT:
            label = "SAT"
            sat += 1
        elif code == _EXIT_UNSAT:
            label = "UNSAT"
            unsat += 1
        else:
            label = f"exit {code}"
            other += 1

        if args.expect:
            exp_sat = args.expect == "sat"
            if code == _EXIT_SAT:
                if exp_sat:
                    matched += 1
                else:
                    mismatched += 1
            elif code == _EXIT_UNSAT:
                if exp_sat:
                    mismatched += 1
                else:
                    matched += 1
            else:
                expect_skipped += 1

        if not args.quiet and not args.dry_run:
            if args.all:
                print("-" * 80)
                extra = _format_perf_extra(
                    elapsed_ms,
                    cpu_s,
                    rss_bytes,
                    show_wall=True,
                    show_cpu=False,
                    show_rss=rss_bytes is not None,
                )
                print(f"{cnf}: {label}{extra}")
                if args.expect and code in (_EXIT_SAT, _EXIT_UNSAT):
                    ok = (code == _EXIT_SAT) == exp_sat
                    print(f"  expected {args.expect.upper()}: {'ok' if ok else 'MISMATCH'}")
            elif args.verbose:
                extra = _format_perf_extra(
                    elapsed_ms,
                    cpu_s,
                    rss_bytes,
                    show_wall=args.metrics,
                    show_cpu=False,
                    show_rss=False,
                )
                print(f"== {cnf} => {label}{extra}")
            else:
                extra = _format_perf_extra(
                    elapsed_ms,
                    cpu_s,
                    rss_bytes,
                    show_wall=args.metrics,
                    show_cpu=args.metrics and cpu_s is not None,
                    show_rss=rss_bytes is not None,
                )
                print(f"{cnf}: {label}{extra}")
                if code not in (_EXIT_SAT, _EXIT_UNSAT) and captured:
                    lines = captured.strip().splitlines()
                    if lines:
                        print(f"  ({lines[-1]})", file=sys.stderr)

    if args.dry_run:
        return 0

    out = sys.stderr if args.quiet else sys.stdout
    total_ms = (time.perf_counter() - total_t0) * 1000.0
    print(
        f"Done: {len(cnf_files)} file(s): {sat} SAT, {unsat} UNSAT, {other} other.",
        file=out,
    )
    if args.all:
        print(f"Total wall time: {total_ms:.2f} ms ({total_ms / 1000.0:.3f} s)", file=out)
    nfiles = len(cnf_files)
    if nfiles and (args.metrics or args.all or args.rss):
        print(f"Avg wall/instance: {sum_wall_ms/nfiles:.2f} ms", file=out)
        if n_cpu:
            print(
                f"Sum MiniSat CPU time (parsed, {n_cpu} run(s)): {sum_cpu_s:.4f} s",
                file=out,
            )
        if max_rss_bytes:
            print(
                f"Peak RSS (max over instances): {max_rss_bytes/1024/1024:.2f} MiB",
                file=out,
            )
    if args.expect:
        compared = matched + mismatched
        pct = (100.0 * matched / compared) if compared else 0.0
        print(
            f"Expected {args.expect.upper()}: matched {matched}, mismatched {mismatched}, "
            f"no SAT/UNSAT verdict (exit other): {expect_skipped}; "
            f"accuracy on verdicts: {matched}/{compared} ({pct:.2f}%)",
            file=out,
        )

    return 1 if other else 0


if __name__ == "__main__":
    raise SystemExit(main())
