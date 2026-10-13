# Graphics text survey

Sources found with `tools/dumpblocks.py` (every Le block -> work/blocks) + `vramfind.py`, catalogued with
`tools/strips.py GROUP OUT.png --sw W --sh H --pal <dump>.pal.bin --pal-index 16+objpal`. Rebuilt items go through
the archive override (asm ArcLookup + build.py OVERRIDE table); generator: `tools/gfx.py`, preview
`tools/gfx_preview.py`.

| # | Screen(s) | What | Source | Format / notes | Status |
|---|---|---|---|---|---|
| 1 | title | logo 機動戦士 ガンダム + ruby シード デスティニー | arc 2.13 tiles, 2.14 map (30x20), 2.15 pal | edited art assets/title_logo_en.png (tools/logo_gen.py, one-off, Windows fonts), re-encoded by tools/logo.py | done |
| 1b | title | ©創通エージェンシー・サンライズ・毎日放送 | arc 2.6 sprites, tiles 0x86-0xC1 | ink 1 / shadow 2 | done |
| 2 | main menu | mode description ticker (9 lines) | arc 3.29 map + 3.28 tiles, 3.32 map + 3.31 tiles | tools/ticker.py | done |
| 3 | MS SELECT, COMMAND SELECT, VS, win quote, RESULT | pilot name plates (28) | arc 4.82-4.109 | 104x8 row; widths table x55 copies | done |
| 4 | MS SELECT, COMMAND SELECT, MS SETTING, VS, NEXT STAGE | MS names (30) | arc 7.20-7.49 | name = tiles 14-27; widths table x55 | done |
| 5 | NEXT STAGE | stage names (25) | arc 4.112-4.136 | 128x16, 4 sprites | done |
| 6 | SHOP | item names (62) | arc 20.12-20.73 | 96x16, 3 sprites, bg 5 | done |
| 7 | VS link | 接続中…… | script 0C7330 | dialogue engine | done |
| 9 | ending | staff roll (6 pages, katakana names) | arc 12.10-12.21 (tiles/map pairs, pal 12.9) | tools/credits.py, Western order, Hepburn | done |
| 8 | CHALLENGE pause | mission text (e.g. 3HITコンボを決めろ!) | sheet ROM 0x704A2C (Le, ref 0x027304; decoded into IWRAM 0x03001BB0, cannot grow) + frame bank table 0x0BB370 (56 sprite frames); composer 0x08027F48.., command lists per MS (Le, table 0x1792D0) advance x via jump table 0x0282E0 | tools/chal.py; missions 2-10 not seen in-game | done (partly verified) |

States: work/states/mainmenu.mss, shop.mss, winquote.mss, fight_start.mss; survey tours work/qa/survey/m1-m8
(cursor routes from mainmenu.mss, see tools/routes/). Challenge pause: work/qa/survey/m5/s001560.mss + START.
