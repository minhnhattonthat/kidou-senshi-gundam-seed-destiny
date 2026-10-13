"""Render archive items as OBJ sprite strips (1D mapping): each item = consecutive SWxSH sprites laid left to right.

    python -X utf8 tools/strips.py GROUP OUT.png [--sw 32 --sh 16] [--pal PAL.bin --pal-index N] [--items a-b]
One row per Le item: label, then the decoded strip. Use it to catalogue name plates, stage names and similar.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import le  # noqa: E402
import textmap as tm  # noqa: E402

GREY = [(0, 128, 0)] + [(255 - 16 * i,) * 3 for i in range(1, 16)]


def palette(path, index):
    if not path:
        return GREY
    d = Path(path).read_bytes()
    out = []
    for i in range(16):
        v = d[(index * 16 + i) * 2] | d[(index * 16 + i) * 2 + 1] << 8
        out.append(((v & 31) * 8, (v >> 5 & 31) * 8, (v >> 10 & 31) * 8))
    return out


def strip(data, sw, sh, pal):
    tw, th = sw // 8, sh // 8
    per = tw * th * 32
    n = max(1, len(data) // per)
    im = Image.new('RGB', (n * sw, sh), pal[0])
    px = im.load()
    for s in range(n):
        for t in range(tw * th):
            base = s * per + t * 32
            ox, oy = s * sw + (t % tw) * 8, (t // tw) * 8
            for y in range(8):
                for x in range(8):
                    if base + y * 4 + x // 2 < len(data):
                        v = data[base + y * 4 + x // 2] >> (4 * (x & 1)) & 15
                        px[ox + x, oy + y] = pal[v]
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('group', type=int)
    ap.add_argument('out')
    ap.add_argument('--sw', type=int, default=32)
    ap.add_argument('--sh', type=int, default=16)
    ap.add_argument('--pal')
    ap.add_argument('--pal-index', type=int, default=0)
    ap.add_argument('--items')
    ap.add_argument('--zoom', type=int, default=2)
    a = ap.parse_args()
    rom = tm.rom()
    pal = palette(a.pal, a.pal_index)
    its = arc.items(rom, arc.groups(rom)[a.group])
    lo, hi = (0, len(its) - 1) if not a.items else map(int, a.items.split('-'))
    rows = []
    for i in range(lo, hi + 1):
        off = its[i]
        if rom[off:off + 2] != b'Le':
            continue
        data, _ = le.decompress(rom, off)
        rows.append(('%d.%d %06X %X' % (a.group, i, off, len(data)), strip(data, a.sw, a.sh, pal)))
    w = min(1600, max(r[1].width for r in rows) * a.zoom + 140)
    sheet = Image.new('RGB', (w, sum(r[1].height * a.zoom + 4 for r in rows)), 'white')
    dr, y = ImageDraw.Draw(sheet), 0
    for label, im in rows:
        dr.text((2, y), label, fill=(255, 0, 0))
        sheet.paste(im.resize((im.width * a.zoom, im.height * a.zoom), Image.NEAREST), (140, y))
        y += im.height * a.zoom + 4
    sheet.save(a.out)
    print(len(rows), 'items')


if __name__ == '__main__':
    main()
