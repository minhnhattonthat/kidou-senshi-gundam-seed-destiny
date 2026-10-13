"""Text lint (hard gate) and fitter.

    python -X utf8 tools/lint.py                     -> lint every translated line; exit 1 on errors
    python -X utf8 tools/lint.py --fit BOX "text"    -> print each displayed line's width (BOX: shop|quote|net)

Limits come from the in-game width gate (docs/re/layout.md): width counts whole 16 px cells per text run.
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import render  # noqa: E402
import textmap as tm  # noqa: E402

TOKEN = re.compile(r'(\{[^}]*\})')
# box: (max px per line, max px for the line the ▼ follows, lines per page)
BOXES = {'shop': (224, 208, 2), 'quote': (224, 208, 3), 'net': (208, 208, 6)}
LAYOUT = {'{n}', '{page}', '{sp6}', '{sp8}'}
JAPANESE = re.compile(r'[　-ヿ一-鿿＀-￯]')
GLOSSARY = ROOT / 'glossary.md'


def box_of(row_id):
    t = row_id.split('_')[0]
    if t == '0C7330':
        return 'net'
    return 'shop' if t in ('0C9530', '0C9A00') else 'quote'


def pages(text):
    """-> [[(line_width_px, followed_by_key), ...] per page] (empty {n} lines skipped)."""
    out, page, cur, has = [], [], 0, False
    parts = [p for p in TOKEN.split(text) if p]
    for i, part in enumerate(parts):
        if part in ('{n}', '{page}', '{key}', '{end}'):
            if has:  # {key} and {page} both wait with the ▼ marker after the text
                page.append([cur, part in ('{key}', '{page}')])
            cur, has = 0, False
            if part == '{page}':
                out.append(page)
                page = []
        elif not part.startswith('{'):
            cur += -(-FONT.width(part) // 16) * 16
            has = True
    if page:
        out.append(page)
    return out


def glossary_terms():
    """(jp, en, avoid) rows from glossary.md tables."""
    terms = []
    if not GLOSSARY.exists():
        return terms
    for ln in GLOSSARY.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        if ln.startswith('|') and len(cells) >= 2 and cells[0] not in ('JP', '') and not set(cells[0]) <= set('-'):
            avoid = [a.strip() for a in cells[4].split(',')] if len(cells) > 4 and cells[4] else []
            terms.append((cells[0], cells[1], avoid))
    return terms


def lint_row(row, terms=()):
    errs, en, jp = [], row['en'], row['jp']
    if JAPANESE.search(en):
        errs.append('Japanese characters left')
    bad = sorted({c for c in TOKEN.sub('', en) if c not in FONT.glyphs and c != ' '})
    if bad:
        errs.append('no glyph for %r' % ''.join(bad))
    cj = collections.Counter(t for t in TOKEN.findall(jp) if t not in LAYOUT)
    ce = collections.Counter(t for t in TOKEN.findall(en) if t not in LAYOUT)
    if cj != ce:
        errs.append('control codes differ: jp-only %s en-only %s' % (dict(cj - ce), dict(ce - cj)))
    if not en.startswith('{n}') or not en.endswith('{end}'):
        errs.append('must start with {n} and end with {end} like the JP')
    if re.search(r'\{num\}(st|nd|rd|th)\b', en):
        errs.append('ordinal suffix after {num}')
    if '{num}' in en and not re.search(r'\{n\}(\{[^}]*\})*\{num\}', en):
        errs.append('{num} must start a line (text runs begin on a 16 px cell)')
    if bad:
        return errs
    full, last, per_page = BOXES[box_of(row['id'])]
    for pi, page in enumerate(pages(en)):
        if len(page) > per_page:
            errs.append('page %d has %d lines (max %d)' % (pi + 1, len(page), per_page))
        for w, key in page:
            lim = last if key else full
            if w > lim:
                errs.append('page %d line %dpx > %dpx' % (pi + 1, w, lim))
    for t_jp, t_en, avoid in terms:
        plain_jp = TOKEN.sub('', jp)
        if t_jp in plain_jp and t_en not in en:
            errs.append('glossary: %s -> %s missing' % (t_jp, t_en))
        for a in avoid:
            if a and re.search(r'\b%s\b' % re.escape(a), en):
                errs.append('glossary: avoid %r' % a)
    return errs


def all_rows():
    for p in sorted((ROOT / 'script').glob('t*.json')):
        yield from json.loads(p.read_text(encoding='utf-8'))


FONT = render.Font(tm.rom())


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--fit':
        box, text = sys.argv[2], sys.argv[3]
        for pi, page in enumerate(pages(text)):
            print('page %d: %s' % (pi + 1, ', '.join('%dpx%s' % (w, ' (key)' if k else '') for w, k in page)))
        print('limits:', BOXES[box])
        return 0
    terms, n, bad = glossary_terms(), 0, 0
    for row in all_rows():
        if not row['en']:
            continue
        n += 1
        errs = lint_row(row, terms)
        if errs:
            bad += 1
            print('%s: %s' % (row['id'], '; '.join(errs)))
    print('%d translated lines, %d with errors' % (n, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
