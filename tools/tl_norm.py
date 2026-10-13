"""Speaker-normalised translation memory: quotes shared by several pilots/suits are translated once.

    python -X utf8 tools/tl_norm.py todo  > work/tl/norm_todo.tsv     normalised JP lines still without a translation
    python -X utf8 tools/tl_norm.py apply work/tl/norm.tsv > work/tl/norm_out.tsv
                                       norm.tsv rows: normalised JP<TAB>normalised EN  ->  key<TAB>EN rows
{f5:xxxxxx} -> {F5}, {f6:xxxxxx} -> {F6}; the line's own codes are put back in order on apply.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = re.compile(r'\{(f5|f6):([0-9A-F]{6})\}')


def norm(jp):
    return CODE.sub(lambda m: '{%s}' % m[1].upper(), jp)


def restore(jp, en_norm):
    codes = {'F5': [], 'F6': []}
    for m in CODE.finditer(jp):
        codes[m[1].upper()].append(m[0])
    out = re.sub(r'\{(F5|F6)\}', lambda m: codes[m[1]].pop(0), en_norm)
    assert not codes['F5'] and not codes['F6'], 'speaker codes left over for %s' % jp
    return out


def unique():
    rows = [ln.split('\t') for ln in (ROOT / 'work/tl/unique.tsv').read_text(encoding='utf-8').splitlines()]
    return [(r[0], r[4]) for r in rows]


def done_keys():
    keys = set()
    for name in ('templates.tsv',):
        p = ROOT / 'work/tl' / name
        if p.exists():
            keys |= {ln.split('\t')[0] for ln in p.read_text(encoding='utf-8').splitlines() if ln}
    return keys


if __name__ == '__main__':
    if sys.argv[1] == 'todo':
        seen, skip = set(), done_keys()
        for key, jp in unique():
            n = norm(jp)
            if key not in skip and n not in seen:
                seen.add(n)
                print(n)
    else:
        tm = dict(ln.split('\t', 1) for ln in Path(sys.argv[2]).read_text(encoding='utf-8').splitlines() if ln)
        skip = done_keys()
        for key, jp in unique():
            if key not in skip and norm(jp) in tm:
                print('%s\t%s' % (key, restore(jp, tm[norm(jp)])))
