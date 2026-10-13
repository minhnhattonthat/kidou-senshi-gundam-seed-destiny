"""Dump the Japanese script to script/<table>.json (one file per pointer table). Never overwrites existing files
unless --force (English lives there).

Entry: id "<table>_<index>", slot (hex offset of the table word), src (hex offset of the JP string), jp, en, status.
Several slots can share a source string; each slot keeps its own entry so lines can diverge.
"""
import argparse
import json
import struct
from pathlib import Path

import textmap as tm

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'script'


def tables(r):
    """[(table_offset, [slot,...])] for every run of consecutive table words in the region."""
    _, _, tw = tm.scan(r)
    groups = []
    for w in sorted(tw):
        if groups and w == groups[-1][1][-1] + 4:
            groups[-1][1].append(w)
        else:
            groups.append((w, [w]))
    return groups


def entries(r):
    strings, _, _ = tm.scan(r)
    out = {}
    for t, slots in tables(r):
        rows = []
        for i, s in enumerate(slots):
            src = struct.unpack_from('<I', r, s)[0] - 0x08000000
            rows.append({'id': '%06X_%03d' % (t, i), 'slot': '%06X' % s, 'src': '%06X' % src,
                         'jp': strings[src][0], 'en': '', 'status': 'todo'})
        out['%06X' % t] = rows
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    SCRIPT.mkdir(exist_ok=True)
    for name, rows in entries(tm.rom()).items():
        p = SCRIPT / ('t%s.json' % name)
        if p.exists() and not a.force:
            continue
        p.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
        print('wrote', p.name, len(rows))


if __name__ == '__main__':
    main()
