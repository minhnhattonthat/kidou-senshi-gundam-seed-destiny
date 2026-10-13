# Graphics text survey

Sources found with `tools/dumpblocks.py` (every Le block -> work/blocks) + `vramfind.py`, catalogued with
`tools/strips.py GROUP OUT.png --sw W --sh H --pal <dump>.pal.bin --pal-index 16+objpal`.

| # | Screen(s) | What | Source | Format | Status |
|---|---|---|---|---|---|
| 1 | title | logo 機動戦士ガンダムSEED DESTINY + ©創通エージェンシー・サンライズ・毎日放送 | TBD | BG | todo |
| 2 | main menu | mode description ticker (9 lines) | arc 3.31 tiles (+ map, pal 3.30) | BG0 4bpp, 512 px lines | todo |
| 3 | MS SELECT, COMMAND SELECT, VS, win quote, RESULT | pilot name plates (28) | arc 4.82-4.109 | 13 tiles = 104x8, OBJ pal 7; fill 2, light 8, outline 1 | todo |
| 4 | MS SELECT, COMMAND SELECT, MS SETTING, VS | MS name strips (30): model no. (EN) + JP name | arc 7.20-7.49 | 28 tiles: 13 model + 15 name (120x8); outline C, fill 2/9 | todo |
| 5 | NEXT STAGE | stage names (25) | arc 4.112-4.136 | 32 tiles = 128x16 (4 sprites 32x16) | todo |
| 6 | SHOP | item list names (タリア・グラディス, 2P ストライク ...) | TBD | | todo |
| 7 | VS link | 接続中…… | script 0C7330 | dialogue engine | done |

States: work/states/mainmenu.mss, shop.mss, winquote.mss, fight_start.mss; survey tours work/qa/survey/m1-m8
(cursor routes from mainmenu.mss, see tools/routes/).
