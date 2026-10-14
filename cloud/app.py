"""Community Cloud entry point for the five-page Cancer Care app."""
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
runpy.run_path(str(ROOT/'prototype.py'),run_name='__main__')
