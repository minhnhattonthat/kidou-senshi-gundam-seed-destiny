"""Rebuilt graphics items (docs/re/graphics.md). build(rom) -> [(group, item, decompressed bytes)].
build.py Le-compresses each, stores it in the expansion area and routes the archive lookup there (ArcLookup).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import le  # noqa: E402
import pixfont  # noqa: E402
import render  # noqa: E402

# arc 4.82-4.109: pilot name plates, 13 tiles (104x8) in one row
PILOTS = {82: 'KIRA YAMATO', 83: 'ATHRUN ZALA', 84: 'DEARKA ELSMAN', 85: 'CLOTHO BUER', 86: 'ORGA SABNAK',
          87: 'SHANI ANDRAS', 88: 'YZAK JOULE', 89: 'NICOL AMALFI', 90: 'RAU LE CREUSET', 91: 'LOWE GUELE',
          92: 'KIRA YAMATO', 93: 'ATHRUN ZALA', 94: 'SHINN ASUKA', 95: 'SHINN ASUKA', 96: 'SHINN ASUKA',
          97: 'STING OAKLEY', 98: 'STELLA LOUSSIER', 99: 'AUEL NEIDER', 100: 'ATHRUN ZALA', 101: 'YZAK JOULE',
          102: 'RAU LE CREUSET', 103: 'RONDO MINA SAHAKU', 104: 'LUNAMARIA HAWKE', 105: 'DEARKA ELSMAN',
          106: 'REY ZA BURREL', 107: 'MU LA FLAGA', 108: 'CAGALLI YULA ATHHA', 109: 'GAI MURAKUMO'}
# arc 7.20-7.49: tiles 0-12 model number (kept), 13 blank, 14-27 name (112x8); later entries are fallbacks
MS = {20: ['STRIKE GUNDAM'], 21: ['AEGIS GUNDAM'], 22: ['BUSTER GUNDAM'], 23: ['RAIDER GUNDAM'],
      24: ['CALAMITY GUNDAM'], 25: ['FORBIDDEN GUNDAM'], 26: ['DUEL GUNDAM'], 27: ['BLITZ GUNDAM'], 28: ['CGUE'],
      29: ['GUNDAM ASTRAY RED FRAME', 'ASTRAY RED FRAME'], 30: ['FREEDOM GUNDAM'], 31: ['JUSTICE GUNDAM'],
      32: ['FORCE IMPULSE GUNDAM'], 33: ['SWORD IMPULSE GUNDAM'], 34: ['BLAST IMPULSE GUNDAM'],
      35: ['CHAOS GUNDAM'], 36: ['GAIA GUNDAM'], 37: ['ABYSS GUNDAM'], 38: ['SAVIOUR GUNDAM'],
      39: ['SLASH ZAKU PHANTOM'], 40: ['PROVIDENCE GUNDAM'],
      41: ['GUNDAM ASTRAY GOLD FRAME AMATSU MINA', 'GOLD FRAME AMATSU MINA'], 42: ['GUNNER ZAKU WARRIOR'],
      43: ['GUNNER ZAKU WARRIOR'], 44: ['BLAZE ZAKU PHANTOM'], 45: ['STRIKE GUNDAM'], 46: ['STRIKE ROUGE'],
      47: ['ASTRAY BLUE FRAME'], 48: ['STRIKE GUNDAM'], 49: ['STRIKE GUNDAM']}


# arc 4.112-4.136: stage names on NEXT STAGE, 128x16 as four 32x16 sprites; centred, outline 1, row gradient
STAGES = {112: 'Heliopolis', 113: 'Archangel Descent', 114: 'Onogoro Island', 115: 'Debris Belt', 116: 'GENESIS',
          117: 'Orb Waters', 118: 'Alaska', 119: 'Orb Battlefield', 120: 'PLANT Interior', 121: 'Panama',
          122: 'North African Desert', 123: 'Colony Mendel', 124: 'North Africa (Dusk)',
          125: 'Onogoro Island(Night)', 126: 'Heliopolis', 127: 'Debris Belt', 128: 'Orb Battlefield',
          129: 'PLANT Interior', 130: 'Lunar Base', 131: 'Artemis', 132: 'Orb Harbor', 133: 'Junius Seven',
          134: 'GENESIS', 135: 'GENESIS', 136: 'GENESIS'}
STAGE_FILL = [2, 9, 9, 8, 8, 8, 9, 9, 2, 2, 2]  # dialogue-font ink rows 2-12, top to bottom


def stage_plate(fnt, text):
    rows = fnt.draw(text)  # 16 rows; ink is D/B/C, the 1 px shadow is 4/7
    w = len(rows[0])
    assert w + 2 <= 128, '%r is %d px' % (text, w + 2)
    ink = [[1 if v in (0xB, 0xC, 0xD) else 0 for v in r] for r in rows]
    ox = (128 - w) // 2
    img = [[0] * 128 for _ in range(16)]
    for y in range(16):
        for x in range(w):
            if ink[y][x] and y >= 1:
                img[y - 1][ox + x] = STAGE_FILL[min(max(y - 2, 0), len(STAGE_FILL) - 1)]
    for y in range(16):
        for x in range(128):
            if not img[y][x] and any(0 <= y + dy < 16 and 0 <= x + dx < 128 and img[y + dy][x + dx] not in (0, 1)
                                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                img[y][x] = 1
    buf = bytearray(1024)
    for s in range(4):
        for t in range(8):
            ox2, oy = s * 32 + (t % 4) * 8, (t // 4) * 8
            for y in range(8):
                for x in range(0, 8, 2):
                    buf[(s * 8 + t) * 32 + y * 4 + x // 2] = img[oy + y][ox2 + x] | img[oy + y][ox2 + x + 1] << 4
    return bytes(buf)


def row_tiles(data, t0, n):
    """8-row pixel strip of tiles t0..t0+n-1 laid left to right."""
    rows = [[0] * (8 * n) for _ in range(8)]
    for t in range(n):
        for y in range(8):
            for x in range(8):
                rows[y][t * 8 + x] = data[(t0 + t) * 32 + y * 4 + x // 2] >> (4 * (x & 1)) & 15
    return rows


def put_tiles(buf, t0, rows):
    n = len(rows[0]) // 8
    for t in range(n):
        for y in range(8):
            for x in range(0, 8, 2):
                buf[(t0 + t) * 32 + y * 4 + x // 2] = rows[y][t * 8 + x] | rows[y][t * 8 + x + 1] << 4


def text_strip(text, style, ntiles):
    img = pixfont.render(text, style)
    w = ntiles * 8
    assert len(img[0]) <= w, '%r is %d px, strip is %d px' % (text, len(img[0]), w)
    rows = [[0] * w for _ in range(8)]
    for y, r in enumerate(img):
        rows[y][:len(r)] = r
    return rows


def fit(names, style, ntiles):
    for name in names:
        if pixfont.width(name) <= ntiles * 8:
            return name
    raise ValueError('no candidate fits %d px: %r' % (ntiles * 8, names))


def build(rom):
    out = []
    for i, name in PILOTS.items():
        data = bytearray(le.decompress(rom, arc.item(rom, 4, i))[0])
        put_tiles(data, 0, text_strip(name, 'pilot', 13))
        out.append((4, i, bytes(data)))
    for i, names in MS.items():
        data = bytearray(le.decompress(rom, arc.item(rom, 7, i))[0])
        # sprites show tiles 14-27 at the name position and tile 13 after them (blank in the JP data)
        put_tiles(data, 14, text_strip(fit(names, 'ms', 14), 'ms', 14))
        out.append((7, i, bytes(data)))
    fnt = render.Font(rom)
    for i, name in STAGES.items():
        out.append((4, i, stage_plate(fnt, name)))
    return out
