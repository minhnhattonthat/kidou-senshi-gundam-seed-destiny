# Kidou Senshi Gundam SEED Destiny (GBA) English translation

Skill: translate-retro-game (H:/translation/kidou-senshi-gundam-seed-destiny/.agents/skills/translate-retro-game/SKILL.md).
Read it before ROM, text or QA work. `$SKILL` below = that directory.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py english` -> build/gsd_en.gba (`identity`, `marker` also)
- Check:    `python -X utf8 tools/check.py` (pytest over tests/; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/gsd_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Table:    `python -X utf8 tools/mktbl.py`; script dump: `python -X utf8 tools/extract.py` (never clobbers, --force)

## Paths
- Original ROM: `rom/1801 - Kidou Senshi Gundam Seed Destiny (J)(Caravan).gba` (gitignored; SHA-1 64eea52c...).
- Emulator: `tools/mesen2/Mesen.exe` + `tools/mesen2/Firmware/gba_bios.bin`; assembler `tools/armips/armips.exe`.
- Text: `script/t<table>.json` (one file per pointer table). Tables: `tbl/`. Glossary + rulings: `glossary.md`.
- RE notes: `docs/re/text.md` (encoding, pointers, renderer, VWF, archive, Le), `docs/re/graphics.md` (survey).
- Graphics: tools/gfx.py (+ticker.py, logo.py, chal.py), preview tools/gfx_preview.py, lint tools/lint.py.
- States: `work/states/` (menu_newgame.mss = NEW GAME/CONTINUE prompt).

## Rulings (user, 2026-10-13)
- Official English names (Shinn Asuka, Athrun Zala...), Western order, no honorifics. Credits in English.
- Full names/terms, engine work before abbreviation. All graphics text in scope (title logo included).
- Pre-approved: keep going through phases, report at milestones.
- Edit source files only with the file-edit tool. ROM <= 16 MiB (EEPROM save).

## Status (2026-10-13)
- Done: script translated + reviewed (514 lines, lint clean); build-time VWF; graphics: logo, copyright, ticker,
  pilot/MS/stage/shop names, CHALLENGE fragments (docs/re/graphics.md). Local release v0.1 in release/ (not published).
- Open: CHALLENGE missions 2-10 not seen in-game; ending/credits not yet checked (god-mode arcade run:
  tools/lua/poke16.lua POKE_ADDR=0x03000D04 POKE_VAL=10240, route work/qa/route_arcade.txt).
- Translation sources: script/t*.json (edit en there), script/tm_norm.tsv + tools/tl_templates.py regenerate them.
