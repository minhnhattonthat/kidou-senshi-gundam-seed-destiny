"""CHALLENGE MODE pause-screen sprites (docs/re/graphics.md #8).

Sheet: Le block at ROM 0x704A2C (code literal at 0x027304), copied to OBJ VRAM tile 0 (sheet tile n = VRAM n).
Frames: pointer table at 0x0BB370 (56 entries) -> u16 count, u16 0, then count records of
    u8 attr0 hi (shape << 6 | flags), u8 attr1 hi (size << 6 | flips), u16 attr2 (tile | pal << 12), s16 x, s16 y.
    python -X utf8 tools/chal.py   -> work/chal_frames.png (every frame rendered with the sheet, greyscale)
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import le  # noqa: E402

SHEET = 0x704A2C
SHEET_REF = 0x027304
TABLE = 0x0BB370
FRAMES = 56
SIZES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
         2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


ADV_TABLE = 0x0282E0      # jump table: frame 0x16+i -> handler that advances the command-list x
ADV_RET = 0x0802837E      # where every handler continues
# frame -> (English, kind). 'cmd' items sit in command lists (x advance patched to fit), 'line' fragments start a
# row at x=32 (<= 208 px), 'tail' fragments follow a number (x computed by the game).
# 'cmd' words are drawn as small caps labels (like the button icons) so their advances stay near the JP ones
TEXT = {
    33: ('BERSERK', 'cmd'), 34: ('BACK', 'cmd'), 35: ('Jump, and before landing do:', 'line'),
    36: (' times!', 'tail'), 37: ('-hit combo!', 'tail'), 38: ('AIR', 'cmd'),
    42: ('Land this combo:', 'line'), 50: ('Counter an attack with:', 'line'),
    52: ('HOLD', 'cmd'), 53: ('MAX CHARGE', 'cmd'), 54: ('TRANSFORM', 'cmd'),
    55: ('Go for max hits!', 'line'),  # 最大HIT数にチャレンジしよう; cells are scarce (sheet cannot grow)
}
LABEL = {46: 'LEVEL'}     # レベル: 24 px before a number at x=32; drawn in the 5 px caps font


def cells_of(rows):
    """16-row pixel rows -> list of 128-byte 16x16 cells (TL, TR, BL, BR tiles)."""
    w = len(rows[0])
    out = []
    for c in range(0, w, 16):
        px = [[rows[y][c + x] if c + x < w else 0 for x in range(16)] for y in range(16)]
        out.append(bytes((px[(k >> 1) * 8 + y][(k & 1) * 8 + x] | px[(k >> 1) * 8 + y][(k & 1) * 8 + x + 1] << 4)
                         for k in range(4) for y in range(8) for x in range(0, 8, 2)))
    return out


def label_rows(text):
    import pixfont
    ink = pixfont.render(text, 'pilot')  # use the glyph shape only
    w = len(ink[0])
    rows = [[0] * (w + 1) for _ in range(16)]
    for y, r in enumerate(ink):
        for x, v in enumerate(r):
            if v not in (0, 1):
                rows[y + 4][x] = 0xD
    for y in range(15, -1, -1):  # dialogue-style shadow: right and below the ink
        for x in range(w, -1, -1):
            if rows[y][x] == 0 and ((x and rows[y][x - 1] == 0xD) or (y and rows[y - 1][x] == 0xD)):
                rows[y][x] = 4
    return rows


def build(rom, fnt, base):
    """-> (blob placed at ROM offset `base`, [(rom offset, bytes)] patches). New sheet, frames and advance stubs."""
    # The sheet is decompressed into IWRAM 0x03001BB0 just below the IWRAM code (0x03005C10): it must not grow.
    # English cells reuse the 16x16 cells that only the replaced Japanese fragments referenced.
    sheet = bytearray(le.decompress(rom, SHEET)[0])
    limit = len(sheet)
    fr = frames(rom)
    replaced = set(TEXT) | set(LABEL)
    kept = set()
    for f, (_, recs) in enumerate(fr):
        if f in replaced:
            continue
        for a0, a1, a2, _, _ in recs:
            w, h = SIZES[a0 >> 6][a1 >> 6]
            kept.update(range(a2 & 1023, (a2 & 1023) + (w // 8) * (h // 8)))
    free = [c for c in range(limit // 128) if not kept & set(range(4 * c, 4 * c + 4))]
    new_frames, adv, placed = {}, {}, {}
    for f, (text, kind) in list(TEXT.items()) + [(k, (v, 'label')) for k, v in LABEL.items()]:
        rows = label_rows(text) if kind in ('label', 'cmd') else fnt.draw(text)
        width = len(rows[0])
        if kind == 'line':
            assert width <= 208, (f, text, width)
        first = sorted(fr[f][1], key=lambda r: r[3])[0]
        pal, x0, y0 = first[2] & 0xF000, first[3], first[4]
        recs = []
        for k, cell in enumerate(cells_of(rows)):
            if not any(cell):
                continue
            if cell in placed:
                c = placed[cell]
            else:
                assert free, 'no free 16x16 cells left in the challenge sheet'
                c = placed[cell] = free.pop(0)
                sheet[c * 128:c * 128 + 128] = cell
            tile = c * 4
            recs.append(struct.pack('<BBHhh', 0x00, 0x40, tile | pal, x0 + 16 * k, y0))
        new_frames[f] = struct.pack('<HH', len(recs), 0) + b''.join(recs)
        if kind == 'cmd':
            adv[f] = width + 2
    assert len(sheet) == limit
    blob, patches = bytearray(), []

    def place(data):
        nonlocal blob
        blob += bytes(-len(blob) % 4)
        off = base + len(blob)
        blob += data
        return off

    packed = le.compress(bytes(sheet))
    patches.append((SHEET_REF, struct.pack('<I', 0x08000000 + place(packed))))
    for f, data in new_frames.items():
        patches.append((TABLE + 4 * f, struct.pack('<I', 0x08000000 + place(data))))
    for f, n in adv.items():
        # adds r6,#n ; ldr r0,[pc,#4] ; bx r0 ; nop ; .word ADV_RET|1  (dispatcher does mov pc,r0: Thumb, even)
        stub = struct.pack('<HHHHI', 0x3600 | n, 0x4801, 0x4700, 0x46C0, ADV_RET | 1)
        patches.append((ADV_TABLE + 4 * (f - 0x16), struct.pack('<I', 0x08000000 + place(stub))))
    return bytes(blob), patches


def frames(rom):
    out = []
    for i in range(FRAMES):
        p = struct.unpack_from('<I', rom, TABLE + 4 * i)[0] - 0x08000000
        n = struct.unpack_from('<H', rom, p)[0]
        out.append((p, [struct.unpack_from('<BBHhh', rom, p + 4 + 8 * k) for k in range(n)]))
    return out


def render(sheet, recs):
    from PIL import Image
    grey = [(0, 96, 0)] + [(255 - 16 * i,) * 3 for i in range(1, 16)]
    boxes = []
    for a0, a1, a2, x, y in recs:
        w, h = SIZES[a0 >> 6][a1 >> 6]
        boxes.append((x, y, w, h, a2 & 1023))
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[0] + b[2] for b in boxes), max(b[1] + b[3] for b in boxes)
    img = Image.new('RGB', (x1 - x0, y1 - y0), (0, 60, 0))
    px = img.load()
    for x, y, w, h, t in boxes:
        tw = w // 8
        for k in range(tw * (h // 8)):
            base = (t + k) * 32
            ox, oy = x - x0 + (k % tw) * 8, y - y0 + (k // tw) * 8
            for yy in range(8):
                for xx in range(8):
                    if base + yy * 4 + xx // 2 < len(sheet):
                        v = sheet[base + yy * 4 + xx // 2] >> (4 * (xx & 1)) & 15
                        if v:
                            px[ox + xx, oy + yy] = grey[v]
    return img


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    import textmap as tm
    rom = tm.rom()
    sheet = le.decompress(rom, SHEET)[0]
    imgs = [render(sheet, recs) for _, recs in frames(rom)]
    z = 2
    H = sum(i.height * z + 4 for i in imgs)
    out = Image.new('RGB', (max(i.width for i in imgs) * z + 40, H), 'white')
    d, y = ImageDraw.Draw(out), 0
    for n, im in enumerate(imgs):
        d.text((2, y), str(n), fill=(255, 0, 0))
        out.paste(im.resize((im.width * z, im.height * z), Image.NEAREST), (40, y))
        y += im.height * z + 4
    out.save(ROOT / 'work/chal_frames.png')
