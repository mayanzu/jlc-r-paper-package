"""Compatibility wrapper; defaults to verification, with no implicit smoke simulation."""
from pathlib import Path
import runpy,sys
if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent/'scripts'))
    if len(sys.argv)==1:sys.argv+=['--mode','verify']
    runpy.run_path(str(Path(__file__).resolve().parent/'scripts/reproduce.py'),run_name='__main__')
