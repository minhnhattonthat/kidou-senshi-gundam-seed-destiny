"""Preview every rebuilt graphics item (tools/gfx.py) next to the original: work/gfx_preview.png."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import arc  # noqa: E402
import gfx  # noqa: E402
import le  # noqa: E402
import strips  # noqa: E402
import textmap as tm  # noqa: E402

LAYOUT = {4: lambda i: (104, 8) if i < 112 else (32, 16), 7: lambda i: (224, 8)}

rom = tm.rom()
rows = []
for g, i, data in gfx.build(rom):
    if g not in LAYOUT:
        continue  # tile+map sets (ticker) are checked in-game
    sw, sh = LAYOUT[g](i)
    old = le.decompress(rom, arc.item(rom, g, i))[0]
    rows.append(('%d.%d' % (g, i), strips.strip(old, sw, sh, strips.GREY), strips.strip(data, sw, sh, strips.GREY)))
z = 2
w = max(r[1].width for r in rows) * z
sheet = Image.new('RGB', (60 + 2 * w + 10, sum(r[1].height * z + 2 for r in rows)), 'white')
dr, y = ImageDraw.Draw(sheet), 0
for label, a, b in rows:
    dr.text((2, y), label, fill=(255, 0, 0))
    sheet.paste(a.resize((a.width * z, a.height * z), Image.NEAREST), (60, y))
    sheet.paste(b.resize((b.width * z, b.height * z), Image.NEAREST), (70 + w, y))
    y += a.height * z + 2
sheet.save(ROOT / 'work/gfx_preview.png')
print(len(rows), 'items')
