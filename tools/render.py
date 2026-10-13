"""Build-time VWF: render each English text run into 16x16 cells and encode them as kanji-bank glyphs (ED xx).

The dialogue renderer draws one OBJ per glyph; ED glyphs come from a bank (u16 offset table + Le blocks) that
asm/main.asm resolves per string (BankForObj: the u32 just before the string). Every string therefore carries its
own bank of pre-rendered cells, and a line costs ceil(width/16) sprites instead of one per letter.

Layout per string: control tokens pass through unchanged; each text run starts on a fresh cell; blank cells inside a
run become two E1 spaces (16 px, no sprite).
"""
import re
import struct

import font
import le

TOKEN = re.compile(r'(\{[^}]*\})')
GAP = 0          # px between glyph ink boxes; the 1 px dark shadow already reads as spacing on the box
SPACE = 3        # px for ' ' (plus the gap after the previous glyph)
CELL = 16
BREAKS = ('{n}', '{page}')


class Font:
    def __init__(self, rom):
        latin, sym, _, codes = font.build(rom)
        self.glyphs = {}
        for ch, code in codes.items():
            src = latin if code < font.FIRST_SYMBOL else sym
            base = (code if code < font.FIRST_SYMBOL else code - font.FIRST_SYMBOL) * 128
            px = font.decode(src[base:base + 128])
            cols = [x for x in range(16) if any(px[y][x] for y in range(16))]
            x0, x1 = cols[0], cols[-1] + 1
            self.glyphs[ch] = ([row[x0:x1] for row in px], x1 - x0)

    def width(self, text):
        w = 0
        for i, ch in enumerate(text):
            w += SPACE if ch == ' ' else self.glyphs[ch][1]
            if i + 1 < len(text):
                w += GAP
        return w

    def draw(self, text):
        """-> 16-row pixel rows of the rendered run."""
        w = self.width(text)
        rows = [[0] * w for _ in range(16)]
        x = 0
        for ch in text:
            if ch == ' ':
                x += SPACE + GAP
                continue
            px, gw = self.glyphs[ch]
            for y in range(16):
                for i, v in enumerate(px[y]):
                    if v:
                        rows[y][x + i] = v
            x += gw + GAP
        return rows


def cells(rows):
    w = len(rows[0]) if rows else 0
    out = []
    for c in range((w + CELL - 1) // CELL):
        px = [[0] * 16 for _ in range(16)]
        for y in range(16):
            seg = rows[y][c * CELL:(c + 1) * CELL]
            px[y][:len(seg)] = seg
        out.append(font.encode(px))
    return out


def line_widths(fnt, text):
    """Pixel width of every displayed line (runs round up to whole cells)."""
    widths, cur = [], 0
    for part in TOKEN.split(text):
        if part in BREAKS:
            widths.append(cur)
            cur = 0
        elif part and not part.startswith('{'):
            cur += -(-fnt.width(part) // CELL) * CELL
    widths.append(cur)
    return widths


def encode(fnt, table, text):
    """-> (string bytes, bank bytes). `table` encodes the control tokens."""
    bank_cells, index, out = [], {}, bytearray()
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith('{'):
            out += table.encode(part)
            continue
        for cell in cells(fnt.draw(part)):
            if not any(cell):
                out += b'\xe1\xe1'
                continue
            if cell not in index:
                index[cell] = len(bank_cells)
                bank_cells.append(cell)
            out += bytes([0xED, index[cell]])
    assert len(bank_cells) <= 256, 'string needs %d cells (max 256)' % len(bank_cells)
    blocks = [le.compress(c) for c in bank_cells]
    head = 2 * len(blocks)
    offs, body = [], bytearray()
    for b in blocks:
        offs.append(head + len(body))
        body += b
    bank = struct.pack('<%dH' % len(offs), *offs) + bytes(body)
    return bytes(out), bank
