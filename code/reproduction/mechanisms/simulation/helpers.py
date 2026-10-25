"""Shared evidence helpers for the consolidated codebase."""
from pathlib import Path
import csv, hashlib, shutil
ROOT = Path(__file__).resolve().parent      # code/simulation
CODE = ROOT.parent                          # code
RESULTS = CODE / 'results'                  # delivered stages


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def snapshot_sources(dest):
    """Copy every *.py in ROOT into dest/'simulation'/'*.py' (no recursion)."""
    target = Path(dest) / 'simulation'
    target.mkdir(parents=True, exist_ok=True)
    for path in ROOT.glob('*.py'):
        shutil.copy2(path, target / path.name)
