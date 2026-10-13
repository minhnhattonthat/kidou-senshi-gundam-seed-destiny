"""Main-menu mode description ticker (docs/re/graphics.md #2).

Two sets: map arc 3.29 (5 lines) with tiles 3.28, map 3.32 (4 lines) with tiles 3.31. Map block: u16 width,
u16 0, u16 height, then 10 more header bytes, then width*height u16 BG entries (tile | pal << 12). Each line is
two tile rows (512x16). English lines are drawn with the dialogue font over the blank bar tiles of each row.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import le  # noqa: E402

SETS = [(29, 28), (32, 31)]  # (map item, tile item) in group 3
LINES = [  # same order as the JP lines; keep each <= MAX_PX so the 512 px loop leaves a gap
    'MAIN MODE: Battle your way through a series of MS piloted by the computer.',
    'VS MODE: Link two Game Boy Advance systems and battle head-to-head.',
    'TRAINING MODE: Practice the basic controls of your MS.',
    'SURVIVAL MODE: See how many computer-piloted MS you can defeat in a row.',
    'CHALLENGE MODE: Clear basic MS actions and combos as instructed.',
    'TIME TRIAL MODE: Beat the computer\'s MS and race for the fastest clear time.',
    'FREE BATTLE MODE: Freely choose the computer\'s MS and the stage, then battle.',
    'OPTIONS: Change the game settings.',
    'SHOP: Trade the POINTS you saved up in each mode for all sorts of things.',
]
MAX_PX = 490
BAR = [0xE, 0xD, 0xF, 0x1] + [0x3] * 10 + [0xD, 0xE]  # background rows of one 16 px line
INK = {0xD: 0xE, 0xC: 0xE, 0xB: 0xE, 0x7: 0x2, 0x4: 0x1}  # dialogue-font colours -> ticker colours


def build(rom, fnt):
    """-> [(group, item, data)] for the two map/tile pairs."""
    out, li = [], 0
    for mi, ti in SETS:
        hdr, w, h, ent, _ = load(rom, mi, ti)
        img = [[BAR[y % 16]] * (w * 8) for y in range(h * 8)]
        for line in range(h // 2):
            text = LINES[li]
            li += 1
            assert fnt.width(text) <= MAX_PX, '%r is %d px' % (text, fnt.width(text))
            rows = fnt.draw(text)
            for y in range(16):
                for x, v in enumerate(rows[y]):
                    if v and 0 <= y + 1 < 16:
                        img[line * 16 + y + 1][x + 1] = INK.get(v, 0xE)
        tiles, index, new = [], {}, []
        for r in range(h):
            for c in range(w):
                t = bytes(img[r * 8 + y][c * 8 + x] | img[r * 8 + y][c * 8 + x + 1] << 4
                          for y in range(8) for x in range(0, 8, 2))
                if t not in index:
                    index[t] = len(tiles)
                    tiles.append(t)
                new.append(0xB000 | (index[t] + 1))  # palette 11, tiles load at VRAM tile 1
        assert len(tiles) < 0x370, 'ticker needs %d tiles' % len(tiles)
        out.append((3, mi, hdr + struct.pack('<%dH' % len(new), *new)))
        out.append((3, ti, b''.join(tiles)))
    return out


def load(rom, mi, ti):
    m = le.decompress(rom, arc.item(rom, 3, mi))[0]
    t = le.decompress(rom, arc.item(rom, 3, ti))[0]
    w, h = struct.unpack_from('<H', m, 0)[0], struct.unpack_from('<H', m, 4)[0]
    ent = list(struct.unpack_from('<%dH' % (w * h), m, 16))
    return m[:16], w, h, ent, t


def pixels(ent, tiles, w, h):
    img = [[0] * (w * 8) for _ in range(h * 8)]
    for r in range(h):
        for c in range(w):
            e = ent[r * w + c]
            t, hf, vf = (e & 1023) - 1, e >> 10 & 1, e >> 11 & 1  # tiles load at VRAM tile 1
            for y in range(8):
                for x in range(8):
                    sx, sy = (7 - x) if hf else x, (7 - y) if vf else y
                    b = t * 32 + sy * 4 + sx // 2
                    img[r * 8 + y][c * 8 + x] = tiles[b] >> (4 * (sx & 1)) & 15 if b < len(tiles) else 0
    return img


if __name__ == '__main__':
    from PIL import Image
    import textmap as tm
    rom = tm.rom()
    pal = [(0, 0, 0)] + [(255 - 16 * i,) * 3 for i in range(1, 16)]
    out = []
    for mi, ti in SETS:
        hdr, w, h, ent, t = load(rom, mi, ti)
        img = pixels(ent, t, w, h)
        print(mi, ti, w, h, 'pal', sorted({e >> 12 for e in ent}), 'colors', sorted({v for r in img for v in r}))
        out += img
    im = Image.new('RGB', (len(out[0]), len(out)))
    for y, r in enumerate(out):
        for x, v in enumerate(r):
            im.putpixel((x, y), pal[v])
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(ROOT / 'work/ticker_orig.png')
