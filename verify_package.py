"""Compatibility entry: verify without running a simulation."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'scripts'))
from verify import verify
if __name__=='__main__':print(json.dumps(verify(),indent=2))
