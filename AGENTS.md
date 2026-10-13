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
- RE notes: `docs/re/text.md` (encoding, pointers, renderer, kerning, archive, Le compression).
- States: `work/states/` (menu_newgame.mss = NEW GAME/CONTINUE prompt).

## Rulings (user, 2026-10-13)
- Official English names (Shinn Asuka, Athrun Zala...), Western order, no honorifics. Credits in English.
- Full names/terms, engine work before abbreviation. All graphics text in scope (title logo included).
- Pre-approved: keep going through phases, report at milestones.
- Edit source files only with the file-edit tool. ROM <= 16 MiB (EEPROM save).

## Status
- Done: setup, recon, table, extraction (514 lines / 30 tables, tests green).
- Next: build.py identity -> font/kern VWF patch -> marker build + width gate -> translate.
