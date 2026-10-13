"""Decompress every "Le" block in the ROM to work/blocks/<offset>.bin (for vramfind.py and graphics hunting).
Also lists them in work/blocks/index.tsv (offset, packed size, unpacked size)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import le  # noqa: E402
import textmap as tm  # noqa: E402


def blocks(rom):
    i = rom.find(b'Le')
    while i >= 0:
        size = rom[i + 2] | rom[i + 3] << 8 | rom[i + 4] << 16
        if rom[i + 5] == 0 and 0 < size < 0x40000:
            try:
                data, used = le.decompress(rom, i)
                yield i, used, data
            except IndexError:
                pass
        i = rom.find(b'Le', i + 1)


if __name__ == '__main__':
    out = ROOT / 'work/blocks'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for off, used, data in blocks(tm.rom()):
        (out / ('%06X.bin' % off)).write_bytes(data)
        rows.append('%06X\t%X\t%X' % (off, used, len(data)))
    (out / 'index.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(len(rows), 'blocks')
