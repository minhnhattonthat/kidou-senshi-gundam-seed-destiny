# Mobile Suit Gundam SEED Destiny (GBA) English translation

Unofficial English fan translation of **Kidou Senshi Gundam SEED Destiny** (Game Boy Advance, Bandai, 2004): the
source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `build.py`, `tools/` | Python build chain: extract, insert, graphics, lint, release. |
| `asm/` | ARM patches assembled with armips (renderer, kerning, archive overrides). |
| `assets/` | Redrawn English graphics (title logo). |
| `tests/` | pytest suite (needs the ROM in `rom/`). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |

## Build your own patched ROM

Needs Python 3.12+ (with Pillow), [armips](https://github.com/Kingcom/armips) at `tools/armips/armips.exe`, and your
own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/kidou-senshi-gundam-seed-destiny
cd kidou-senshi-gundam-seed-destiny
# copy your dump to: rom/1801 - Kidou Senshi Gundam Seed Destiny (J)(Caravan).gba
#   (8388608 bytes, SHA-1 64eea52cd909669a972c091869c5f47865863bc0; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py english                        # -> build/gsd_en.gba
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Bandai's and is included only so the
translation can be checked against it. Mobile Suit Gundam SEED Destiny is (c) Sotsu Agency, Sunrise, MBS; the game is
(c) Bandai. This project is not affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
