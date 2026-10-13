"""Layout-test builds: override whole tables or single lines with ruler text, keeping each line's leading controls.

    python -X utf8 tools/qa_build.py OUT.gba --tables 0CB070,0CB2C0 --lines 224,224,208 [--key]
Each listed table's lines become: <original leading control tokens> L1 ruler {n} L2 ruler ... [{key}]{end}
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import build  # noqa: E402
import render  # noqa: E402

LEAD = re.compile(r'^((?:\{[^}]*\})*)')


def ruler(fnt, width, prefix):
    s = prefix + ' '.join('%d.Wide' % i for i in range(1, 40))
    while -(-fnt.width(s) // 16) * 16 > width:
        s = s[:-1]
    return s.rstrip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--tables', required=True)
    ap.add_argument('--lines', default='224,224,208')
    ap.add_argument('--key', action='store_true', help='end with {key} (A-button wait) instead of plain {end}')
    ap.add_argument('--text', help='use this body instead of rulers (control tokens allowed)')
    a = ap.parse_args()
    fnt = render.Font(build.tm.rom())
    body = a.text or '{n}'.join(ruler(fnt, int(w), 'L%d:' % (i + 1)) for i, w in enumerate(a.lines.split(',')))
    tail = ('{key}' if a.key else '') + '{end}'
    qa = {}
    for t in a.tables.split(','):
        for row in json.loads((ROOT / 'script' / ('t%s.json' % t)).read_text(encoding='utf-8')):
            qa[row['id']] = LEAD.match(row['jp'])[1] + body + tail
    Path(a.out).write_bytes(build.build('marker', qa))
    print(next(iter(qa.values())))


if __name__ == '__main__':
    main()
