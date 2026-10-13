import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import extract  # noqa: E402
import le  # noqa: E402
import textmap as tm  # noqa: E402

R = tm.rom()
STRINGS, SLOTS, TABLE_WORDS = tm.scan(R)


def test_region_fully_covered():
    assert tm.coverage(R, STRINGS, TABLE_WORDS) == []


def test_every_string_roundtrips():
    for off, (text, n) in STRINGS.items():
        assert '[' not in text, '%06X has unknown bytes: %s' % (off, text)
        assert tm.JP.encode(text) == R[off:off + n], '%06X' % off


def test_counts():
    assert len(STRINGS) == 514 and len(TABLE_WORDS) == 514
    assert len(extract.tables(R)) == 30


def test_script_json_matches_rom():
    want = extract.entries(R)
    files = sorted((ROOT / 'script').glob('t*.json'))
    assert [p.stem[1:] for p in files] == sorted(want)
    for p in files:
        rows = json.loads(p.read_text(encoding='utf-8'))
        ref = want[p.stem[1:]]
        assert [(x['id'], x['slot'], x['src'], x['jp']) for x in rows] == \
               [(x['id'], x['slot'], x['src'], x['jp']) for x in ref], p.name


def test_le_codec_roundtrip_font_blocks():
    for gi, ii in ((6, 9), (6, 10), (6, 11)):
        data, _ = le.decompress(R, arc.item(R, gi, ii))
        assert le.decompress(le.compress(data), 0)[0] == data
