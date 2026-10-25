"""Portable package paths; all generated outputs are outside frozen inputs."""
from pathlib import Path
import os

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'docs/paper_audit'
TECH=ROOT/'docs/technical_documentation'
MAIN=Path(os.environ.get('JLCR_PAPER_ROOT',str(ROOT/'docs/manuscript_source'))).resolve()
FIGURES=ROOT/'assets/paper_figures'
def output_root(value=None):
    if value:return Path(value).resolve()
    project=ROOT.parent.parent/'JLC-R'
    if (project/'AGENTS.md').is_file():return project/'temp/minimal_reproduction'
    return ROOT/'outputs'
