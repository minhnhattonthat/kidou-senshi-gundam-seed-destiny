"""Title logo (BG1 on the title screen): tiles arc 2.13 (loaded at VRAM tile 1), map 2.14 (30x20, 16-byte
header, u16 entries tile|hflip<<10|vflip<<11|pal<<12), palettes 2.15 (raw 8x16 BGR555).

    decode(rom) -> PIL RGB image 240x160
    encode(rom, img) -> (tiles bytes, map bytes) for the archive override: each 8x8 cell takes the logo palette
    that matches it best, pixels snap to that palette, identical tiles are shared.
The English artwork lives in assets/title_logo_en.png (made once by tools/logo_gen.py, then hand-checked).
"""
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import le  # noqa: E402

W, H = 30, 20


def palettes(rom):
    off = arc.item(rom, 2, 15)  # 8 raw BGR555 palettes (2.12 is the all-black fade palette)
    out = []
    for p in range(8):
        row = []
        for i in range(16):
            v = struct.unpack_from('<H', rom, off + (p * 16 + i) * 2)[0]
            row.append(((v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3))
        out.append(row)
    return out


def load(rom):
    tiles = le.decompress(rom, arc.item(rom, 2, 13))[0]
    m = le.decompress(rom, arc.item(rom, 2, 14))[0]
    return tiles, m[:16], list(struct.unpack_from('<%dH' % (W * H), m, 16))


def decode(rom):
    tiles, _, ent = load(rom)
    pals = palettes(rom)
    img = Image.new('RGB', (W * 8, H * 8))
    px = img.load()
    for r in range(H):
        for c in range(W):
            e = ent[r * W + c]
            t, hf, vf, p = (e & 1023) - 1, e >> 10 & 1, e >> 11 & 1, e >> 12
            for y in range(8):
                for x in range(8):
                    sx, sy = (7 - x) if hf else x, (7 - y) if vf else y
                    v = tiles[t * 32 + sy * 4 + sx // 2] >> (4 * (sx & 1)) & 15 if t >= 0 else 0
                    px[c * 8 + x, r * 8 + y] = pals[p][v] if v else (0, 0, 0)
    return img


def used_palettes(rom):
    return sorted({e >> 12 for e in load(rom)[2]})


def encode(rom, img):
    orig_tiles, hdr, orig_ent = load(rom)
    pals = palettes(rom)
    cand = used_palettes(rom)
    px = img.convert('RGB').load()
    opx = decode(rom).load()
    tiles = [orig_tiles[i:i + 32] for i in range(0, len(orig_tiles), 32)]  # block tile k = VRAM tile k+1
    index, ent = {}, []

    def dist(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b))

    for r in range(H):
        for c in range(W):
            cell = [px[c * 8 + x, r * 8 + y] for y in range(8) for x in range(8)]
            if cell == [opx[c * 8 + x, r * 8 + y] for y in range(8) for x in range(8)]:
                ent.append(orig_ent[r * W + c])
                continue
            if not any(v != (0, 0, 0) for v in cell):
                ent.append(0)
                continue
            best = None
            for p in cand:
                idx, err = [], 0
                for rgb in cell:
                    if rgb == (0, 0, 0):
                        idx.append(0)
                        continue
                    k = min(range(1, 16), key=lambda i: dist(pals[p][i], rgb))
                    idx.append(k)
                    err += dist(pals[p][k], rgb)
                if best is None or err < best[0]:
                    best = (err, p, idx)
            _, p, idx = best
            t = bytes(idx[i] | idx[i + 1] << 4 for i in range(0, 64, 2))
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            ent.append((index[t] + 1) | p << 12)
    assert len(tiles) + 1 <= 0x200, 'logo needs %d tiles (BG1 char block holds 512)' % (len(tiles) + 1)
    return b''.join(tiles), hdr + struct.pack('<%dH' % len(ent), *ent)


if __name__ == '__main__':
    import textmap as tm
    decode(tm.rom()).save(ROOT / 'work/title_logo_jp.png')
    print('palettes', used_palettes(tm.rom()))
