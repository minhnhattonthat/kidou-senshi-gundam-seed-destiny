"""One-off generator for assets/title_logo_en.png (needs Windows fonts; the build only reads the PNG).

Erases 機動戦士 / ガンダム / the ruby over DESTINY from the decoded logo and draws MOBILE SUIT + GUNDAM in the
logo's silver/blue style. Boxes are logo pixel coordinates (240x160 map, logo occupies the top ~64 rows).
    python -X utf8 tools/logo_gen.py [--preview]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import logo  # noqa: E402
import textmap as tm  # noqa: E402

FONTS = Path('C:/Windows/Fonts')
GLOW = (240, 248, 248)
KATAKANA_BOX = (20, 19, 111, 54)      # ガンダム (stops before the big S)
KANJI_BOX = (84, 9, 132, 21)          # 機動戦士 (dark pixels only, so the S survives)
RUBY_BOX = (165, 33, 214, 37)         # シード デスティニー, red on white between the S and DESTINY


def fill(img, box, pred=lambda rgb: True):
    px = img.load()
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if px[x, y] != (0, 0, 0) and pred(px[x, y]):
                px[x, y] = GLOW


def text_layer(text, font, size, shear):
    f = ImageFont.truetype(str(FONTS / font), size)
    w, h = f.getbbox(text)[2] + 8, f.getbbox(text)[3] + 8
    mask = Image.new('L', (w, h))
    ImageDraw.Draw(mask).text((4, 0), text, font=f, fill=255)
    if shear:
        mask = mask.transform((w + int(h * shear), h), Image.AFFINE, (1, shear, -h * shear, 0, 1, 0),
                              resample=Image.BICUBIC)
    return mask.point(lambda v: 255 if v > 110 else 0)


def gundam(img):
    big = text_layer('GUNDAM', 'impact.ttf', 152, 0.25)  # 4x supersampled, then reduced
    big = big.crop(big.getbbox())
    bw, bh = KATAKANA_BOX[2] - KATAKANA_BOX[0] - 6, KATAKANA_BOX[3] - KATAKANA_BOX[1] - 6
    mask = big.resize((bw, bh), Image.LANCZOS).point(lambda v: 255 if v > 120 else 0)
    ox, oy = KATAKANA_BOX[0] + 3, KATAKANA_BOX[1] + 3
    outline = mask.filter(ImageFilter.MaxFilter(5))
    inner = mask.filter(ImageFilter.MaxFilter(3))
    px, m, o, i = img.load(), mask.load(), outline.load(), inner.load()
    for y in range(bh):
        t = y / max(1, bh - 1)
        silver = tuple(int(a + (b - a) * t) for a, b in zip((248, 248, 252), (150, 156, 196)))
        for x in range(bw):
            if m[x, y]:
                px[ox + x, oy + y] = silver
            elif i[x, y]:
                px[ox + x, oy + y] = (88, 96, 200)
            elif o[x, y]:
                px[ox + x, oy + y] = (32, 32, 104)


def mobile_suit(img):
    import pixfont
    rows = pixfont.render('MOBILE SUIT', 'pilot')  # 7 rows incl. outline; draw ink only, dark on a glow plate
    w = len(rows[0])
    ox, oy = 104 - w // 2, 11
    px = img.load()
    for y in range(-1, 8):
        for x in range(-2, w + 2):
            px[ox + x, oy + y] = GLOW
    for y, r in enumerate(rows):
        for x, v in enumerate(r):
            if v not in (0, 1):
                px[ox + x, oy + y] = (16, 16, 32)


def main():
    img = logo.decode(tm.rom())
    fill(img, KATAKANA_BOX)
    fill(img, KANJI_BOX, lambda rgb: sum(rgb) < 330)
    fill(img, RUBY_BOX, lambda rgb: min(rgb) < 200)
    gundam(img)
    mobile_suit(img)
    out = ROOT / 'assets/title_logo_en.png'
    out.parent.mkdir(exist_ok=True)
    img.save(out)
    if '--preview' in sys.argv:
        img.crop((0, 0, 240, 72)).resize((960, 288), Image.NEAREST).save(ROOT / 'work/title_logo_en_z.png')
    print('wrote', out)


if __name__ == '__main__':
    main()
