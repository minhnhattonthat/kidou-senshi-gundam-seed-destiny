# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 - release v1.0 prepared locally in `release/` (2026-10-19); not published on GitHub Releases yet.
- **Done:** script translated + reviewed (514 lines, lint clean); build-time VWF; graphics: logo, copyright, ticker,
  pilot/MS/stage/shop names, CHALLENGE fragments (`docs/re/graphics.md`); staff roll (`tools/credits.py`), checked
  in-game from the arcade ending (god mode: `tools/lua/poke16.lua` POKE_ADDR=0x03000D04 POKE_VAL=10240; ending state
  `work/qa/ending/s008400.mss`, local). Repo follows fan-translation-template (README, rom.sha1, docs).
- **Next:** publish the release when the user says so.
- **Open bugs:** CHALLENGE missions 2-10 not seen in-game (locked until cleared); listed in the release README.
- **Waiting on the user:** publishing the GitHub release.
- Translation sources: `script/t*.json` (edit en there); `script/tm_norm.tsv` + `tools/tl_templates.py` regenerate them.
