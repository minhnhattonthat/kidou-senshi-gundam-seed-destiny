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
import chal  # noqa: E402
import gfx  # noqa: E402
import le  # noqa: E402
import render  # noqa: E402
import textmap as tm  # noqa: E402
from tbl import Table  # noqa: E402

BUILD = ROOT / 'build'
ARMIPS = ROOT / 'tools/armips/armips.exe'
SIZE = 0x1000000          # 16 MiB: EEPROM save addressing breaks above this
CODE = 0x0C7340           # asm code, in the freed string block 0xC7340-0xC9530 (BL range of the renderer)
KERN = 0x800000           # kern table
OVERRIDE = 0x800800       # archive overrides: u8 group, u8 item, u16 0, u32 address; FF ends (256 max)
TEXT = 0x801000           # strings and their cell banks, then rebuilt graphics (tools/gfx.py)
# bytes the English build may change outside the expansion area (romdiff gate)
PATCHED = [(0x000CAC, 0x000CB4), (0x031BEC, 0x031BF0), (0x031EA8, 0x031EAC), (0x032550, 0x032558),
           (0x0325F2, 0x0325FA), tm.REGION,
           (0x027304, 0x027308), (0x0282E0, 0x0282E0 + 33 * 4), (0x0BB370, 0x0BB370 + 56 * 4)]  # tools/chal.py


def allowed_ranges(orig):
    """PATCHED plus every name-width table copy (romdiff gate)."""
    return PATCHED + [(off, off + len(data)) for off, data in gfx.width_patches(orig)]
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


def build(mode, qa=None):
    """qa: {id: text} overrides for single-line layout tests (build.py MODE --qa ID=TEXT ...)."""
    qa = qa or {}
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
        text = qa.get(row['id']) or (marker_text(row, fnt) if mode == 'marker' else row['en'])
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
    ov = bytearray()
    for g, i, data in gfx.build(orig):
        packed = le.compress(data)
        put(rom, at, packed)
        ov += struct.pack('<BBHI', g, i, 0, 0x08000000 + at)
        at = (at + len(packed) + 3) & ~3
    for off, data in gfx.width_patches(orig):
        put(rom, off, data)
    blob, patches = chal.build(orig, fnt, at)  # CHALLENGE pause-screen mission fragments
    put(rom, at, blob)
    at = (at + len(blob) + 3) & ~3
    for off, data in patches:
        put(rom, off, data)
    assert len(ov) < TEXT - OVERRIDE - 8
    put(rom, OVERRIDE, ov + b'\xff' * 8)
    assert at <= SIZE, 'text overflows the ROM'
    BUILD.mkdir(exist_ok=True)
    tmp = BUILD / '_asm.gba'
    tmp.write_bytes(rom)
    cmd = [str(ARMIPS), str(ROOT / 'asm/main.asm'), '-strequ', 'ROM', str(tmp),
           '-definelabel', 'CodeBase', hex(0x08000000 + CODE), '-definelabel', 'OverrideTable',
           hex(0x08000000 + OVERRIDE), '-definelabel', 'KernTable',
           hex(0x08000000 + KERN), '-erroronwarning']
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        raise SystemExit('armips failed:\n' + res.stdout + res.stderr)
    out = tmp.read_bytes()
    tmp.unlink()
    return out


def main():
    args = sys.argv[1:]
    mode = args.pop(0) if args and not args[0].startswith('--') else 'english'
    names = {'identity': 'gsd_identity.gba', 'english': 'gsd_en.gba', 'marker': 'gsd_marker.gba'}
    if mode not in names:
        raise SystemExit(__doc__)
    qa = {}
    while args:
        flag = args.pop(0)
        if flag != '--qa' or not args:
            raise SystemExit(__doc__)
        k, _, v = args.pop(0).partition('=')
        qa[k] = v
    name = names[mode] if not qa else names[mode].replace('.gba', '_qa.gba')
    BUILD.mkdir(exist_ok=True)
    out = build(mode, qa)
    (BUILD / name).write_bytes(out)
    print('wrote', BUILD / name, hex(len(out)))


if __name__ == '__main__':
    main()
