"""Resource archive at ROM 0x787970 (lookup routine 0x08000CAC: group(r0), item(r1)).

Top: u32 offsets (from the archive base) per group; first offset / 4 = group count.
Group: u16 offsets (from the group start) per item; first offset / 2 = item count.
Items are often "Le" blocks (le.py) or nested u16 tables (font banks: group 6 items 12, 13).
"""
import struct

BASE = 0x787970


def groups(rom):
    n = struct.unpack_from('<I', rom, BASE)[0] // 4
    return [BASE + o for o in struct.unpack_from('<%dI' % n, rom, BASE)]


def items(rom, g):
    n = struct.unpack_from('<H', rom, g)[0] // 2
    return [g + o for o in struct.unpack_from('<%dH' % n, rom, g)]


def item(rom, gi, ii):
    return items(rom, groups(rom)[gi])[ii]


if __name__ == '__main__':
    import sys
    rom = open(sys.argv[1], 'rb').read()
    for gi, g in enumerate(groups(rom)):
        its = items(rom, g)
        print('group %2d @%06X  %d items' % (gi, g, len(its)))
        for ii, a in enumerate(its):
            print('   %2d.%-3d @%06X %s' % (gi, ii, a, rom[a:a + 6].hex(' ')))
