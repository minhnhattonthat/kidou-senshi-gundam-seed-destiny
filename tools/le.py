"""The game's "Le" LZ codec (IWRAM routine at 0x03005C10, ROM caller 0x08001A84).

Block: 'L' 'e' size24(LE) 00, then groups: one flag byte = four 2-bit ops, LSB first:
  0: u16 v -> copy (v>>12)+3 bytes from out[-((v&0xFFF)+5)]
  1: u8 c  -> copy (c>>2)+2 bytes from out[-((c&3)+1)]
  2: 1 literal byte      3: 3 literal bytes
Decoding stops when size bytes are out (mid-group is fine).
"""


def decompress(rom, off):
    assert rom[off:off + 2] == b'Le', 'no Le header at %X' % off
    size = rom[off + 2] | rom[off + 3] << 8 | rom[off + 4] << 16
    src, out = off + 6, bytearray()
    while len(out) < size:
        flags = rom[src]
        src += 1
        for _ in range(4):
            if len(out) >= size:
                break
            op = flags & 3
            flags >>= 2
            if op == 2:
                out.append(rom[src])
                src += 1
            elif op == 3:
                out += rom[src:src + 3]
                src += 3
            else:
                if op == 0:
                    v = rom[src] | rom[src + 1] << 8
                    src += 2
                    dist, n = (v & 0xFFF) + 5, (v >> 12) + 3
                else:
                    c = rom[src]
                    src += 1
                    dist, n = (c & 3) + 1, (c >> 2) + 2
                for _ in range(n):
                    out.append(out[-dist])
    return bytes(out), src - off


def compress(data):
    """Greedy encoder; output always decodes back to data (lengths never overrun the size)."""
    out = bytearray(b'Le' + bytes([len(data) & 255, len(data) >> 8 & 255, len(data) >> 16 & 255, 0]))
    ops, i = [], 0
    while i < len(data):
        best_n, best_d = 0, 0
        for d in range(1, min(i, 0xFFF + 5) + 1):
            n = 0
            lim = min(len(data) - i, 18 if d >= 5 else 65)
            while n < lim and data[i + n] == data[i + n - d]:
                n += 1
            if n > best_n:
                best_n, best_d = n, d
        if best_d <= 4 and best_n >= 2:
            n = min(best_n, 65)
            ops.append((1, bytes([(n - 2) << 2 | (best_d - 1)])))
            i += n
        elif best_d >= 5 and best_n >= 3:
            n = min(best_n, 18)
            v = (n - 3) << 12 | (best_d - 5)
            ops.append((0, bytes([v & 255, v >> 8])))
            i += n
        elif i + 3 <= len(data) and len(data) - i >= 3:
            ops.append((3, data[i:i + 3]))
            i += 3
        else:
            ops.append((2, data[i:i + 1]))
            i += 1
    for g in range(0, len(ops), 4):
        grp = ops[g:g + 4]
        out.append(sum(op << (2 * k) for k, (op, _) in enumerate(grp)))
        for _, payload in grp:
            out += payload
    return bytes(out)
