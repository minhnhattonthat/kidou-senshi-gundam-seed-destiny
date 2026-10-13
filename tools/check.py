"""One-command check: every test under tests/. The pre-commit hook runs this; exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.exit(subprocess.call([sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', str(ROOT / 'tests')], cwd=ROOT))
