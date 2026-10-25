"""Run the agricultural extension experiments (supply scan, freshness, canopy).

Usage:
  python -B run_extension.py --task supply --workers 10
  python -B run_extension.py --task freshness --workers 10
  python -B run_extension.py --task canopy --workers 10

Results are appended per completed run so an interrupted sweep can resume.
The frozen 480-run confirmation is never overwritten: the freshness task writes
a new file that is checked against the published metrics.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import extension_core as core  # noqa: E402

RESULTS = HERE / "results"


def design():
    return core.load_design()


def design_key(task):
    return {"supply": "supply_scan"}.get(task, task)


def seeds_for(task):
    entry = design()["seeds"][design_key(task)]
    return [entry["start"] + entry["step"] * k for k in range(entry["count"])]


def cases(task):
    d = design()
    key = design_key(task)
    out = []
    for condition in d["conditions"][key]:
        for supply in d["supplies"][key]:
            for seed in seeds_for(task):
                for method in d["methods"][key]:
                    if task == "canopy":
                        for treatment in d["canopy"]["treatments"]:
                            out.append((task, condition, seed, supply, method, treatment))
                    else:
                        out.append((task, condition, seed, supply, method, "C0"))
    return out


def read_existing(path):
    if not path.exists():
        return [], set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    keys = {(r["task"], r["condition"], int(r["seed"]), float(r["supply"]),
             r["canopy_treatment"], r["method"]) for r in rows}
    return rows, keys


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=core.FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance(task, path, requested, skipped):
    d = design()
    record = {
        "task": task,
        "design": d,
        "frozen_implementation": d["frozen_implementation"],
        "days": d["days"],
        "executions_requested": requested,
        "executions_skipped_as_existing": skipped,
        "executions_in_file": sum(1 for _ in csv.DictReader(path.open(encoding="utf-8-sig"))),
        "output": path.name,
        "output_sha256": sha(path),
        "frozen_source_sha256": {
            name: sha(core.SIM / name)
            for name in ["simulator.py", "v63_model.py", "v6_model.py",
                         "optimized_model.py", "v4_diagnostics.py",
                         "canopy_model.py", "current_io.py", "current_design.json"]
        },
        "python": sys.version.split()[0],
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (RESULTS / f"{task}_provenance.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, choices=["supply", "freshness", "canopy"])
    parser.add_argument("--workers", type=int, default=max(1, min(10, (os.cpu_count() or 2) - 2)))
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=0, help="Optional cap for a smoke test; 0 runs the full task.")
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    path = args.output or RESULTS / f"{args.task}.csv"
    path = path if path.is_absolute() else HERE / path
    rows, done = read_existing(path)
    todo = []
    for case in cases(args.task):
        key = (case[0], case[1], case[2], case[3], case[5], case[4])
        if key not in done:
            todo.append(case)
    print(f"{args.task}: {len(todo)} runs to execute, {len(done)} already present", flush=True)
    if args.limit:
        todo = todo[:args.limit]
        print(f"  smoke-test limit: {len(todo)} runs", flush=True)
    if not todo:
        provenance(args.task, path, len(cases(args.task)), len(done))
        return
    started = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(core.run_case, *case): case for case in todo}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            rows.append(row)
            if index % 10 == 0 or index == len(todo):
                write_rows(path, sorted(rows, key=lambda r: (r["condition"], float(r["supply"]),
                                                             r["canopy_treatment"], int(r["seed"]),
                                                             r["method"])))
                elapsed = time.time() - started
                rate = index / elapsed if elapsed else float("inf")
                print(f"  {index}/{len(todo)} complete ({rate:.2f} runs/s)", flush=True)
    write_rows(path, sorted(rows, key=lambda r: (r["condition"], float(r["supply"]),
                                                 r["canopy_treatment"], int(r["seed"]),
                                                 r["method"])))
    record = provenance(args.task, path, len(cases(args.task)), len(done))
    print(json.dumps({k: record[k] for k in ["task", "executions_in_file", "output", "output_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
