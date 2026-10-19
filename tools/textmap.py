"""Map the Japanese script region: strings, the pointer slots that reach them, local pointer tables, padding.

Region REGION is a run of strings and 4-byte pointer tables (0x08000000|offset). Strings are found as targets of
aligned ROM words; every byte of the region must be a string, a table word or 00 padding (coverage test).
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tbl import Table  # noqa: E402

ORIG = ROOT / 'rom/1801 - Kidou Senshi Gundam Seed Destiny (J)(Caravan).gba'
REGION = (0xC72F0, 0xCC9A8)
JP = Table.load(ROOT / 'tbl/jp.tbl')


def rom():
    return ORIG.read_bytes()


def scan(r):
    """-> (strings {off: (text, length)}, slots {off: [slot,...]}, table_words set of slot offsets inside REGION)."""
    lo, hi = REGION
    # Only words inside the region count: every string is reached from a local table, and the few outside
    # words that equal a region address are graphics/data that land mid-string (checked: 6 such, none real).
    slots = {}
    for s in range(lo, hi, 4):
        t = struct.unpack_from('<I', r, s)[0] - 0x08000000
        if lo <= t < hi:
            slots.setdefault(t, []).append(s)
    table_words = {s for v in slots.values() for s in v}
    strings = {}
    for t in sorted(slots):
        if t in table_words:
            continue
        text, n = JP.decode(r, t)
        strings[t] = (text, n)
    # targets that are themselves table words (a pointer to a table inside the region) are not strings
    return strings, {t: s for t, s in slots.items() if t in strings}, table_words


def coverage(r, strings, table_words):
    """Byte ranges inside REGION not explained by a string, a table word or zero padding."""
    lo, hi = REGION
    used = bytearray(hi - lo)
    for t, (_, n) in strings.items():
        for k in range(t, t + n):
            used[k - lo] = 1
    for s in table_words:
        for k in range(s, s + 4):
            used[k - lo] = 1
    gaps, k = [], 0
    while k < len(used):
        if not used[k] and r[lo + k] != 0:
            j = k
            while j < len(used) and not used[j]:
                j += 1
            gaps.append((lo + k, lo + j))
            k = j
        else:
            k += 1
    return gaps


if __name__ == '__main__':
    r = rom()
    strings, slots, tw = scan(r)
    print('strings', len(strings), 'table words', len(tw), 'outside slots',
          sum(1 for v in slots.values() for s in v if not REGION[0] <= s < REGION[1]))
    for a, b in coverage(r, strings, tw):
        print('GAP %06X-%06X %s' % (a, b, JP.decode(r, a, b - a)[0][:80]))
