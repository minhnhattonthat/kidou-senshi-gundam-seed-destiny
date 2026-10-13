"""Deduplicate frames (sheet.py --changed logic, Pillow) and write paged full-size contact sheets with labels.

    python -X utf8 tools/pages.py SRC_DIR OUT_PREFIX [--changed 0.10] [--per 12] [--cols 3]
"""
import argparse
import glob
import os

from PIL import Image, ImageChops, ImageDraw


def diff(a, b):
    d = ImageChops.difference(a, b).convert('L').point(lambda v: 255 if v > 24 else 0)
    return sum(d.histogram()[255:]) / (a.width * a.height)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out')
    ap.add_argument('--changed', type=float, default=0.10)
    ap.add_argument('--per', type=int, default=12)
    ap.add_argument('--cols', type=int, default=3)
    a = ap.parse_args()
    kept, last = [], None
    for f in sorted(glob.glob(os.path.join(a.src, 'f*.png'))):
        im = Image.open(f).convert('RGB')
        if last is None or diff(im, last) > a.changed:
            kept.append((os.path.basename(f)[1:-4], im))
            last = im
    for p in range(0, len(kept), a.per):
        chunk = kept[p:p + a.per]
        rows = (len(chunk) + a.cols - 1) // a.cols
        sheet = Image.new('RGB', (a.cols * 244, rows * 174), 'white')
        dr = ImageDraw.Draw(sheet)
        for i, (name, im) in enumerate(chunk):
            x, y = (i % a.cols) * 244, (i // a.cols) * 174
            sheet.paste(im, (x, y + 12))
            dr.text((x + 2, y), name, fill=(255, 0, 0))
        sheet.save('%s_%02d.png' % (a.out, p // a.per))
    print(len(kept), 'kept ->', (len(kept) + a.per - 1) // a.per, 'pages')


if __name__ == '__main__':
    main()
