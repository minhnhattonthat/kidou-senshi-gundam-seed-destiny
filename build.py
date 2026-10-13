"""Build entry point.

    python -X utf8 build.py identity   -> build/gsd_identity.gba (no edits; must equal the original)
    python -X utf8 build.py english    -> build/gsd_en.gba
    python -X utf8 build.py marker     -> build/gsd_marker.gba (every line = its id + filler, for layout QA)

Every script string is re-emitted in the expansion area, 4-aligned, preceded by the address of its glyph bank:
English lines are pre-rendered into 16x16 cells (tools/render.py), untranslated lines keep the kanji bank (6.12).
"""
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / '.agents/skills/translate-retro-game/scripts'))
import arc  # noqa: E402
import render  # noqa: E402
import textmap as tm  # noqa: E402
from tbl import Table  # noqa: E402

BUILD = ROOT / 'build'
ARMIPS = ROOT / 'tools/armips/armips.exe'
SIZE = 0x1000000          # 16 MiB: EEPROM save addressing breaks above this
CODE = 0x0C7340           # asm code, in the freed string block 0xC7340-0xC9530 (BL range of the renderer)
KERN = 0x800000           # kern table
TEXT = 0x801000           # strings and their cell banks
# bytes the English build may change outside the expansion area (romdiff gate)
PATCHED = [(0x031BEC, 0x031BF0), (0x031EA8, 0x031EAC), (0x032550, 0x032558), (0x0325F2, 0x0325FA), tm.REGION]
FILLER = 'The quick brown fox jumps over the lazy dog 0123456789'
TOKEN = re.compile(r'(\{[^}]*\})')


def script_rows():
    rows = []
    for p in sorted((ROOT / 'script').glob('t*.json')):
        rows += json.loads(p.read_text(encoding='utf-8'))
    return rows


def marker_text(row, fnt, width=208):
    """Keep every control token; replace each run of text with the line id (first run) or filler, cut to width."""
    parts, out, first = TOKEN.split(row['jp']), [], True
    table, idx = row['id'].split('_')
    for part in parts:
        if not part or part.startswith('{'):
            out.append(part)
        else:
            s = ('%s.%d %s' % (table[1:], int(idx), FILLER)) if first else FILLER[:len(part) * 2]
            while fnt.width(s) > width:
                s = s[:-1]
            out.append(s.rstrip())
            first = False
    return ''.join(out)


def put(rom, off, data):
    rom[off:off + len(data)] = data


def build(mode):
    orig = tm.rom()
    rom = bytearray(orig)
    if mode == 'identity':
        return bytes(rom)
    rom += b'\xff' * (SIZE - len(rom))
    kt = bytes(b for i in range(256) for b in (0xED, i, 0)) + orig[0xC7244:0xC72EB]  # orig table, FF at 0xC72EA
    assert kt[-1] == 0xFF and KERN + len(kt) <= TEXT
    put(rom, KERN, kt)
    # every string moves; clear the old ones (only table words point at them, textmap.scan)
    strings, _, _ = tm.scan(orig)
    for off, (_, n) in strings.items():
        rom[off:off + n] = bytes(n)
    en = Table.load(ROOT / 'tbl/en.tbl')
    fnt = render.Font(orig)
    kanji = 0x08000000 + arc.item(orig, 6, 12)
    at, placed = TEXT, {}
    for row in script_rows():
        text = marker_text(row, fnt) if mode == 'marker' else row['en']
        if text:
            data, bank = render.encode(fnt, en, text)
        else:
            data, bank = tm.JP.encode(row['jp']), None
        key = (data, bank)
        if key not in placed:
            if bank is None:
                bank_addr = kanji
            else:
                bank_addr = 0x08000000 + at
                put(rom, at, bank)
                at = (at + len(bank) + 3) & ~3
            put(rom, at, struct.pack('<I', bank_addr) + data)
            placed[key] = at + 4
            at = (at + 4 + len(data) + 3) & ~3
        struct.pack_into('<I', rom, int(row['slot'], 16), 0x08000000 + placed[key])
    assert at <= SIZE, 'text overflows the ROM'
    BUILD.mkdir(exist_ok=True)
    tmp = BUILD / '_asm.gba'
    tmp.write_bytes(rom)
    cmd = [str(ARMIPS), str(ROOT / 'asm/main.asm'), '-strequ', 'ROM', str(tmp),
           '-definelabel', 'CodeBase', hex(0x08000000 + CODE), '-definelabel', 'KernTable',
           hex(0x08000000 + KERN), '-erroronwarning']
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        raise SystemExit('armips failed:\n' + res.stdout + res.stderr)
    out = tmp.read_bytes()
    tmp.unlink()
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'english'
    names = {'identity': 'gsd_identity.gba', 'english': 'gsd_en.gba', 'marker': 'gsd_marker.gba'}
    if mode not in names:
        raise SystemExit(__doc__)
    BUILD.mkdir(exist_ok=True)
    out = build(mode)
    (BUILD / names[mode]).write_bytes(out)
    print('wrote', BUILD / names[mode], hex(len(out)))


if __name__ == '__main__':
    main()
