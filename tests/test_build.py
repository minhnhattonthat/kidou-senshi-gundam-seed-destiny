import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

ROMDIFF = ROOT / '.agents/skills/translate-retro-game/scripts/romdiff.py'


def test_identity_build_is_byte_identical():
    assert build.build('identity') == build.tm.rom()


def test_marker_build_writes_only_allowed_ranges(tmp_path):
    out = tmp_path / 'm.gba'
    out.write_bytes(build.build('marker'))
    ranges = ['%X-%X' % (a, b - 1) for a, b in build.allowed_ranges(build.tm.rom())] + ['800000-FFFFFF']
    res = subprocess.run([sys.executable, str(ROMDIFF), str(build.tm.ORIG), str(out), *ranges],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
