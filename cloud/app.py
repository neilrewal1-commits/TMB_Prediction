"""Community Cloud entry point. Experience release: patient journeys and research story, v0.4."""
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
runpy.run_path(str(ROOT/'prototype.py'),run_name='__main__')
