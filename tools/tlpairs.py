"""Translation work files.

    python -X utf8 tools/tlpairs.py dump  -> work/tl/unique.tsv: one row per distinct JP line
                                             (key<TAB>ids<TAB>box<TAB>speaker<TAB>jp), key = first id
    python -X utf8 tools/tlpairs.py merge work/tl/X.tsv  -> sets en (and status=done) for every id whose JP equals
                                             the keyed line's JP. Input rows: key<TAB>english.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'script'
# speaker portrait index ({f5}/{f6} third byte) -> pilot, from the win-quote tables (docs/re/text.md)
PILOTS = ['Kira (Strike)', 'Athrun (Aegis)', 'Dearka (Buster)', 'Clotho (Raider)', 'Orga (Calamity)',
          'Shani (Forbidden)', 'Yzak (Duel)', 'Nicol (Blitz)', 'Rau (CGUE)', 'Lowe (Astray)', 'Kira (Freedom)',
          'Athrun (Justice)', 'Shinn (Force Impulse)', 'Shinn (Sword Impulse)', 'Shinn (Blast Impulse)',
          'Sting (Chaos)', 'Stella (Gaia)', 'Auel (Abyss)', 'Athrun (Saviour)', 'Yzak (Slash ZAKU Phantom)',
          'Rau (Providence)', 'Mina (Gold Frame Amatsu Mina)', 'Lunamaria (Gunner ZAKU Warrior)',
          'Dearka (Gunner ZAKU Warrior?)', 'Rey (Blaze ZAKU Phantom)', 'Mu (?)', 'Cagalli (?)']


def box(table):
    if table == '0C7330':
        return 'net'
    return 'shop' if table in ('0C9530', '0C9A00') else 'quote'


def rows():
    out = []
    for p in sorted(SCRIPT.glob('t*.json')):
        out += [(p, r) for r in json.loads(p.read_text(encoding='utf-8'))]
    return out


def dump():
    seen = {}
    for p, r in rows():
        seen.setdefault(r['jp'], []).append(r['id'])
    d = ROOT / 'work/tl'
    d.mkdir(parents=True, exist_ok=True)
    lines = []
    for jp, ids in seen.items():
        t = ids[0].split('_')[0]
        sp = ''
        if '{f5:0000' in jp:
            i = int(jp.split('{f5:0000')[1][:2], 16)
            sp = PILOTS[i] if i < len(PILOTS) else '#%d' % i
        lines.append('\t'.join([ids[0], ','.join(ids), box(t), sp, jp]))
    (d / 'unique.tsv').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(len(lines), 'unique lines')


def merge(path):
    tl = {}
    for ln in Path(path).read_text(encoding='utf-8').splitlines():
        if ln.strip():
            k, _, en = ln.partition('\t')
            tl[k] = en
    jp_of = {r['id']: r['jp'] for _, r in rows()}
    by_jp = {jp_of[k]: en for k, en in tl.items()}
    files = {}
    for p, r in rows():
        files.setdefault(p, []).append(r)
        if r['jp'] in by_jp:
            r['en'], r['status'] = by_jp[r['jp']], 'done'
    for p, rs in files.items():
        p.write_text(json.dumps(rs, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print('merged', len(tl), 'keys')


if __name__ == '__main__':
    {'dump': dump, 'merge': lambda: merge(sys.argv[2])}[sys.argv[1]]()
