"""Rebuilt graphics items (docs/re/graphics.md). build(rom) -> [(group, item, decompressed bytes)].
build.py Le-compresses each, stores it in the expansion area and routes the archive lookup there (ArcLookup).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import credits  # noqa: E402
import le  # noqa: E402
import logo  # noqa: E402
import pixfont  # noqa: E402
import render  # noqa: E402
import ticker  # noqa: E402

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
          122: 'North African Desert', 123: 'Colony Mendel', 124: 'North Africa (Dawn)',
          125: 'Onogoro Island(Night)', 126: 'Heliopolis', 127: 'Debris Belt', 128: 'Orb Battlefield',
          129: 'PLANT Interior', 130: 'Lunar Base', 131: 'Artemis', 132: 'Orb Harbor', 133: 'Junius Seven',
          134: 'GENESIS', 135: 'GENESIS', 136: 'GENESIS'}
STAGE_FILL = [2, 9, 9, 8, 8, 8, 9, 9, 2, 2, 2]  # dialogue-font ink rows 2-12, top to bottom


# arc 20.12-20.73: SHOP item names, 96x16 as three 32x16 sprites, bg index 5 (41 and 53 are blank)
SHOP = {12: '2P STRIKE', 13: '2P AEGIS', 14: '2P BUSTER', 15: '2P RAIDER', 16: '2P CALAMITY',
        17: '2P FORBIDDEN', 18: '2P DUEL', 19: '2P BLITZ', 20: '2P CGUE', 21: '2P ASTRAY RED FRAME',
        22: '2P FREEDOM', 23: '2P JUSTICE', 24: '2P FORCE IMPULSE', 25: '2P SWORD IMPULSE', 26: '2P BLAST IMPULSE',
        27: '2P CHAOS', 28: '2P GAIA', 29: '2P ABYSS', 30: '2P SAVIOUR', 31: '2P SLASH ZAKU PHANTOM',
        32: '2P PROVIDENCE', 33: '2P GOLD FRAME AMATSU MINA', 34: '2P GUNNER ZAKU WARRIOR',
        35: '2P BLAZE ZAKU PHANTOM', 36: 'LUNAR BASE', 37: 'ARTEMIS', 38: 'ORB HARBOR', 39: 'JUNIUS SEVEN',
        40: 'AME-NO-MIHASHIRA', 42: 'NORTH AFRICA (DAWN)', 43: 'ONOGORO ISLAND (NIGHT)', 44: 'SOUND MODE',
        45: 'VERY HARD MODE', 46: 'INFINITE THRUSTER', 47: 'INFINITE PS', 48: 'INFINITE SUPER SPECIALS',
        49: 'LACUS OUTFIT A', 50: 'LACUS OUTFIT B', 51: 'LACUS OUTFIT C', 52: 'LACUS OUTFIT D',
        54: 'US GUNDAM SEED', 55: 'MS CALAMITY', 56: 'MS RAIDER', 57: 'MS FORBIDDEN', 58: 'MS SAVIOUR',
        59: 'MS SWORD IMPULSE', 60: 'MS BLAST IMPULSE', 61: 'MS SLASH ZAKU PHANTOM', 62: 'CAGALLI YULA ATHHA',
        63: 'MU LA FLAGA', 64: 'DEARKA ELSMAN', 65: 'MS GOLD FRAME AMATSU MINA', 66: 'MS PROVIDENCE',
        67: 'MS FREEDOM', 68: 'MS JUSTICE', 69: 'PINK HARO', 70: 'NAVY HARO', 71: 'GILBERT DURANDAL',
        72: 'NEO ROANOKE', 73: 'TALIA GLADYS'}


def split2(text, w):
    """One line if it fits in w px, else the most balanced two-line split that fits."""
    if pixfont.width(text) <= w:
        return [text]
    words = text.split(' ')
    best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        m = max(pixfont.width(a), pixfont.width(b))
        if m <= w and (best is None or m < best[0]):
            best = (m, [a, b])
    assert best, '%r does not fit two lines of %d px' % (text, w)
    return best[1]


def sprites_bytes(img, nspr):
    """16-row image -> nspr 32x16 sprites in 1D tile order (4 tiles top row, 4 bottom)."""
    buf = bytearray(nspr * 256)
    for s in range(nspr):
        for t in range(8):
            ox, oy = s * 32 + (t % 4) * 8, (t // 4) * 8
            for y in range(8):
                for x in range(0, 8, 2):
                    buf[(s * 8 + t) * 32 + y * 4 + x // 2] = img[oy + y][ox + x] | img[oy + y][ox + x + 1] << 4
    return bytes(buf)


def shop_name(text):
    lines = split2(text, 96)
    img = [[5] * 96 for _ in range(16)]
    top = 4 if len(lines) == 1 else 1
    for n, line in enumerate(lines):
        rows = pixfont.render(line, 'shop')
        ox = (96 - len(rows[0])) // 2
        for y, r in enumerate(rows):
            for x, v in enumerate(r):
                if v:
                    img[top + n * 7 + y][ox + x] = v
    return sprites_bytes(img, 3)


# arc 2.6 title-screen sprites: the copyright line is tiles 0x86-0xC1 (seven 32x16 + one 16x16 at y=136);
# ink 1, shadow 2, rows 3-12. The (C) glyph (x < 28) and rows 13-15 (top of the next line) are kept.
COPYRIGHT = 'SOTSU AGENCY・SUNRISE・MBS'


def copyright_strip(rom, fnt):
    data = bytearray(le.decompress(rom, arc.item(rom, 2, 6))[0])

    def cells():
        for s in range(8):
            w = 4 if s < 7 else 2
            for t in range(w * 2):
                yield 0x86 + (s * 8 if s < 7 else 56) + t, s * 32 + (t % w) * 8, (t // w) * 8

    rows = fnt.draw(COPYRIGHT)
    assert 30 + len(rows[0]) <= 240
    img = [[0] * 240 for _ in range(16)]
    for tile, ox, oy in cells():
        for y in range(8):
            for x in range(8):
                img[oy + y][ox + x] = data[tile * 32 + y * 4 + x // 2] >> (4 * (x & 1)) & 15
    for y in range(13):
        for x in range(28, 240):
            img[y][x] = 0
    for y in range(16):
        for x, v in enumerate(rows[y]):
            if v and 0 <= y + 1 < 13:
                img[y + 1][30 + x] = 2 if v in (4, 7) else 1
    for tile, ox, oy in cells():
        for y in range(8):
            for x in range(0, 8, 2):
                data[tile * 32 + y * 4 + x // 2] = img[oy + y][ox + x] | img[oy + y][ox + x + 1] << 4
    return bytes(data)


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
    return sprites_bytes(img, 4)


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


# Name widths in px used to place the strips (the win-quote plate is right-aligned by it). They are static
# arrays from a C header, so ~55 compilation units each carry a copy; every copy is patched.
MS_WIDTHS = 0xCD172      # first copy: 30 bytes, arc 7.20-7.49, width of the name from tile 14
PILOT_WIDTHS = 0xCD190   # first copy: 28 bytes, arc 4.82-4.109


def width_patches(rom):
    """-> [(rom offset, bytes)] for every copy of the name width tables."""
    ms = bytes(pixfont.width(fit(MS[i], 'ms', 14)) for i in sorted(MS))
    pilots = bytes(pixfont.width(PILOTS[i]) for i in sorted(PILOTS))
    out = []
    for first, en in ((MS_WIDTHS, ms), (PILOT_WIDTHS, pilots)):
        jp = rom[first:first + len(en)]
        i = rom.find(jp, 0xC0000, 0xE0000)
        while i >= 0:
            out.append((i, en))
            i = rom.find(jp, i + 1, 0xE0000)
    return out


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
    out += ticker.build(rom, fnt)
    out += credits.build(rom, fnt)
    for i, name in SHOP.items():
        out.append((20, i, shop_name(name)))
    out.append((2, 6, copyright_strip(rom, fnt)))
    art = ROOT / 'assets/title_logo_en.png'  # made by tools/logo_gen.py
    if art.exists():
        from PIL import Image
        tiles, tmap = logo.encode(rom, Image.open(art))
        out += [(2, 13, tiles), (2, 14, tmap)]
    return out
