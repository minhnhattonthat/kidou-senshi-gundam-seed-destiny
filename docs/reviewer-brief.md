# Translation reviewer brief - Kidou Senshi Gundam SEED Destiny (GBA, 2005)

You review the JP->EN fan translation of a Gundam SEED / SEED Destiny 2D fighter. Read-only: no edits, no git,
no subagents. Mechanical validity (control codes, widths, ASCII) is already enforced by `tools/lint.py` - judge
translation quality.

## Inputs
- `work/tl/review_pairs.txt`: every distinct line as `>> id | box | speaker` then `JP:` and `EN:`. Read ALL of it
  (about 100 KB: read it in passes with offset/limit).
- `glossary.md` (rulings at the top). Official Bandai English names; Western order; no honorifics.
- Context: `shop` lines are spoken by a shopkeeper (Lacus: gentle, polite; Cagalli: blunt, boyish; Azrael: smarmy,
  "heh heh heh"); they unlock/describe shop items. `quote` lines are post-fight win quotes: `{f5:..}` is the winner
  speaking, text after `{page}{n}{n}{f6:XXXXXX}` is the loser replying (XXXXXX = portrait index; the speaker list
  is PILOTS in tools/tlpairs.py, index 0 = Kira (Strike)). `{key}` waits for a button; `{n}` is a line break.
- The speaker field for quotes is the *winner*. Known portrait indices: 00 Kira, 01 Athrun, 02 Dearka, 03 Clotho,
  04 Orga, 05 Shani, 06 Yzak, 07 Nicol, 08 Rau (CGUE), 09 Lowe, 0A Kira (Freedom), 0B Athrun (Justice),
  0C-0E Shinn, 0F Sting, 10 Stella, 11 Auel, 12 Athrun (Saviour), 13 Yzak (Slash ZAKU), 14 Rau (Providence),
  15 Rondo Mina Sahaku, 16 Lunamaria, 17 Dearka (ZAKU), 18 Rey, 19 Mu La Flaga, 1A Cagalli.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; voice per character (anime-faithful).
- Things players catch: jokes/references losing their punch (Haro's "omae mo na", Mu's "I'll be right back",
  Rey's "気にするな"), awkward stock phrases, wrong pronoun gender for the replying speaker.
- Naturalness: would a fan-translation reader stumble?
- Do NOT propose longer lines casually: boxes are tight. If you suggest new EN, keep it about the same length.

## Report: write it to `work/tl/review.md` with your file-write tool, then reply with only the counts
### Critical (meaning reversed, wrong speaker/addressee)
### Important (clear mistranslation, glossary/voice inconsistency, unnatural enough to stumble)
### Minor (style; deferred to one polish pass)
Each item: `id - JP gist - problem - suggested EN (full line with control codes)`.
### Assessment
Approved | Needs fixes - one sentence why.
