"""Community Cloud entry point for Cancer Care, including its welcome page."""
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
runpy.run_path(str(ROOT/'prototype.py'),run_name='__main__')
