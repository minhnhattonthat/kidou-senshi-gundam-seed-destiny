"""5 px caps pixel font with 1 px outline, for the small name strips (pilot plates, MS names).

render(text, style) -> rows (list of lists of palette indices), 7 rows tall (outline, 5 glyph rows, outline),
placed inside an 8 px tile row by the caller. Styles give the outline index and a per-row fill gradient taken from
the game's own strips (docs/re/graphics.md).
"""
GLYPHS = {
    'A': '.##.|#..#|####|#..#|#..#', 'B': '###.|#..#|###.|#..#|###.', 'C': '.###|#...|#...|#...|.###',
    'D': '###.|#..#|#..#|#..#|###.', 'E': '####|#...|###.|#...|####', 'F': '####|#...|###.|#...|#...',
    'G': '.###|#...|#.##|#..#|.###', 'H': '#..#|#..#|####|#..#|#..#', 'I': '###|.#.|.#.|.#.|###',
    'J': '..##|...#|...#|#..#|.##.', 'K': '#..#|#.#.|##..|#.#.|#..#', 'L': '#...|#...|#...|#...|####',
    'M': '#...#|##.##|#.#.#|#...#|#...#', 'N': '#..#|##.#|#.##|#..#|#..#', 'O': '.##.|#..#|#..#|#..#|.##.',
    'P': '###.|#..#|###.|#...|#...', 'Q': '.##.|#..#|#..#|#.##|.###', 'R': '###.|#..#|###.|#.#.|#..#',
    'S': '.###|#...|.##.|...#|###.', 'T': '###|.#.|.#.|.#.|.#.', 'U': '#..#|#..#|#..#|#..#|.##.',
    'V': '#...#|#...#|.#.#.|.#.#.|..#..', 'W': '#...#|#...#|#.#.#|##.##|#...#', 'X': '#..#|#..#|.##.|#..#|#..#',
    'Y': '#.#|#.#|.#.|.#.|.#.', 'Z': '####|...#|.##.|#...|####',
    '0': '###|#.#|#.#|#.#|###', '1': '.#.|##.|.#.|.#.|###', '2': '###|..#|###|#..|###', '3': '###|..#|###|..#|###',
    '4': '#.#|#.#|###|..#|..#', '5': '###|#..|###|..#|###', '6': '###|#..|###|#.#|###', '7': '###|..#|..#|.#.|.#.',
    '8': '###|#.#|###|#.#|###', '9': '###|#.#|###|..#|###', '-': '...|...|###|...|...', '.': '.|.|.|.|#',
    '/': '..#|..#|.#.|#..|#..', "'": '#|#|.|.|.', '(': '.#|#.|#.|#.|.#', ')': '#.|.#|.#|.#|#.',
    '&': '.#..|#.#.|.#..|#.#.|.##.', '!': '#|#|#|.|#', '?': '###|..#|.##|...|.#.',
}
SPACE = 2
# style: (outline index, fill per glyph row 0-4)
STYLES = {
    'pilot': (1, [2, 2, 2, 2, 8]),           # arc 4.82+: white fill, grey foot, dark outline
    'ms': (0xC, [0xA, 0x9, 0xB, 0x2, 0x2]),  # arc 7.20+: same chrome gradient as the model numbers
}


def width(text):
    w = 1  # left outline
    for ch in text:
        w += SPACE if ch == ' ' else len(GLYPHS[ch].split('|')[0]) + 1
    return w


def render(text, style):
    outline, fill = STYLES[style]
    w = width(text)
    ink = [[0] * w for _ in range(7)]
    x = 1
    for ch in text:
        if ch == ' ':
            x += SPACE
            continue
        rows = GLYPHS[ch].split('|')
        for y, row in enumerate(rows):
            for i, c in enumerate(row):
                if c == '#':
                    ink[y + 1][x + i] = 1
        x += len(rows[0]) + 1
    out = [[0] * w for _ in range(7)]
    for y in range(7):
        for x in range(w):
            if ink[y][x]:
                out[y][x] = fill[y - 1]
            elif any(0 <= y + dy < 7 and 0 <= x + dx < w and ink[y + dy][x + dx]
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                out[y][x] = outline
    return out
