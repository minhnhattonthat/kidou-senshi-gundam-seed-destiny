# Kidou Senshi Gundam SEED Destiny (GBA) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, here `C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game`; tools/release.py and tests read the `SKILL` env var, else that path). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py english` -> build/gsd_en.gba (`identity`, `marker` also; checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py` (pytest over tests/; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/gsd_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Release:  `python -X utf8 tools/release.py --version <v>` (patch + verify; never publish without the user)
- Table:    `python -X utf8 tools/mktbl.py`; script dump: `python -X utf8 tools/extract.py` (never clobbers, --force)

## Paths
- Original ROM: `rom/1801 - Kidou Senshi Gundam Seed Destiny (J)(Caravan).gba` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`).
- Emulator: `tools/mesen2/Mesen.exe` + `tools/mesen2/Firmware/gba_bios.bin`; assembler `tools/armips/armips.exe` (gitignored). States: `work/states/` (menu_newgame.mss = NEW GAME/CONTINUE prompt).
- Text: `script/t<table>.json` (one file per pointer table). Tables: `tbl/` (codec `tools/tbl.py`, copied from the skill). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Graphics: tools/gfx.py (+ticker.py, logo.py, chal.py, credits.py), preview tools/gfx_preview.py, lint tools/lint.py.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- ROM <= 16 MiB (EEPROM save addressing).
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
