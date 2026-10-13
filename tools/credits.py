"""Staff roll (ending): six pages, each a tile block + map block in archive group 12 (tiles 12.10/12/14/16/18/20,
maps 12.11/13/15/17/19/21; 16-byte header w=30 h=32, u16 entries; tiles load at VRAM tile 1).

    python -X utf8 tools/credits.py   -> work/credits_jp.png (all pages decoded, greyscale by index)
English pages: PAGES below is the source text (one entry per JP line, same rows); build() redraws every page with
the dialogue font at the JP line positions and re-tiles it.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import le  # noqa: E402

SETS = [(10, 11), (12, 13), (14, 15), (16, 17), (18, 19), (20, 21)]
W, H = 30, 32


# One entry per JP text line, top to bottom (Western name order, Hepburn without macrons)
PAGES = [
    ['Produced by BANDAI', 'Executive Producer', 'Shin Unozawa', 'General Producer', 'Takashi Shoji',
     'Chief Producers', 'Fuyuki Nishizawa', 'Yoshiyasu Horiuchi', 'Producer', 'Makoto Nishizawa',
     'Assistant Producer'],
    ['Satoshi Ono', 'Promotion Producer', 'Hirotaka Watanabe', 'Developed by NATSUME', 'Producer',
     'Mitsuo Matsumoto', 'Director', 'Yoichi Arakawa'],
    ['Programmers', 'Masashi Ueda', 'Yuji Tanabe', 'Artwork', 'Satoshi Ueda', 'Atsushi Fukushima',
     'Natsuko Asano', 'Yoichi Arakawa', 'Sound', 'Iku Mizutani', 'Tetsuari Watanabe', 'Special Thanks',
     'Toshifumi Onishi'],
    ['Kiyoshi Shimizu', 'Tomoaki Imanishi', 'Toshihiro Suzuki', 'Norihiko Ushimura', 'Yoshitaka Goto',
     'Masaki Hoshiai', 'SUNRISE', 'Hiroyuki Sato', 'Akihiro Morita', 'Koji Nakajima'],
    ['Kaori Shida', 'Toshiaki Baba', 'CRUISE', 'Sadayoshi Fujino', 'Chizuko Maruyama', 'Yuji Kawanabe'],
    ['Special Thanks', 'Toshifumi Onishi', 'Kiyoshi Shimizu', 'Sadayoshi Fujino', 'Chizuko Maruyama',
     'Yuji Kawanabe'],
]
INK = {0xD: 3, 0xC: 3, 0xB: 3, 0x4: 1, 0x7: 2}  # dialogue-font colours -> credit colours


def line_starts(img):
    rows = [y for y in range(len(img)) if any(img[y])]
    return [y for y in rows if y - 1 not in rows]


def build(rom, fnt):
    """-> [(12, item, data)] for every page's tiles and map."""
    out = []
    for (ti, mi), lines in zip(SETS, PAGES):
        tiles, hdr, ent = load(rom, ti, mi)
        jp = pixels(tiles, ent)
        starts = line_starts(jp)
        assert len(starts) == len(lines), 'page %d: %d JP lines, %d EN' % (ti, len(starts), len(lines))
        img = [[0] * (W * 8) for _ in range(H * 8)]
        for y0, text in zip(starts, lines):
            x0 = min(x for y in range(y0, y0 + 12) for x in range(W * 8) if jp[y][x])
            rows = fnt.draw(text)
            assert x0 + len(rows[0]) <= W * 8, (text, len(rows[0]))
            for y in range(2, 16):
                for x, v in enumerate(rows[y]):
                    if v and y0 + y - 2 < H * 8:
                        img[y0 + y - 2][x0 + x] = INK.get(v, 3)
        new_tiles, index, new_ent = [], {}, []
        for r in range(H):
            for c in range(W):
                t = bytes(img[r * 8 + y][c * 8 + x] | img[r * 8 + y][c * 8 + x + 1] << 4
                          for y in range(8) for x in range(0, 8, 2))
                if not any(t):
                    new_ent.append(0)
                    continue
                if t not in index:
                    index[t] = len(new_tiles)
                    new_tiles.append(t)
                new_ent.append(0x1000 | (index[t] + 1))  # palette 1; block tile k = VRAM tile k+1
        assert len(new_tiles) + 1 <= 384, 'credits page needs %d tiles' % len(new_tiles)
        out.append((12, ti, b''.join(new_tiles)))
        out.append((12, mi, hdr + struct.pack('<%dH' % len(new_ent), *new_ent)))
    return out


def load(rom, ti, mi):
    t = le.decompress(rom, arc.item(rom, 12, ti))[0]
    m = le.decompress(rom, arc.item(rom, 12, mi))[0]
    return t, m[:16], list(struct.unpack_from('<%dH' % (W * H), m, 16))


def pixels(tiles, ent):
    img = [[0] * (W * 8) for _ in range(H * 8)]
    for r in range(H):
        for c in range(W):
            e = ent[r * W + c]
            t, hf, vf = (e & 1023) - 1, e >> 10 & 1, e >> 11 & 1
            if t < 0:
                continue
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
    pages = []
    for ti, mi in SETS:
        t, _, ent = load(rom, ti, mi)
        img = pixels(t, ent)
        print(ti, mi, 'pal', sorted({e >> 12 for e in ent}), 'colours', sorted({v for r in img for v in r}))
        pages.append(img)
    out = Image.new('RGB', (W * 8 * 3 + 20, H * 8 * 2 + 10), 'red')
    for n, img in enumerate(pages):
        ox, oy = (n % 3) * (W * 8 + 10), (n // 3) * (H * 8 + 10)
        for y, row in enumerate(img):
            for x, v in enumerate(row):
                out.putpixel((ox + x, oy + y), pal[v])
    out.save(ROOT / 'work/credits_jp.png')
