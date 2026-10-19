# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `tools/font.py` (built from the ROM) | the game's own Latin and symbol glyph banks (archive 6.10, 6.13) | the game's | yes, as a diff against the user's own dump | dialogue, ticker, staff roll | re-aligned into a proportional font; digits/punctuation added in the same colours |
| `tools/pixfont.py` | drawn for this project | MIT, same as repo | yes | pilot/MS/stage/shop name strips, CHALLENGE text | - |
| `assets/title_logo_en.png` | drawn by `tools/logo_gen.py` with Windows Impact (`impact.ttf`) | Impact: Monotype, Windows font | yes, as rendered pixel art only (the font file is not shipped) | "GUNDAM" in the title logo | supersampled, sheared, recoloured to the logo palette |
