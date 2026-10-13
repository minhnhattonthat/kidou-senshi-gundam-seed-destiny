"""Print a test line of at most N px (whole cells) for --qa layout tests: python tools/ruler.py 224 [prefix]"""
import sys

import render
import textmap as tm

fnt = render.Font(tm.rom())
width, prefix = int(sys.argv[1]), (sys.argv[2] if len(sys.argv) > 2 else '')
s = prefix + ' '.join('%d.Wide' % i for i in range(1, 40))
while -(-fnt.width(s) // 16) * 16 > width:
    s = s[:-1]
print(s.rstrip())
