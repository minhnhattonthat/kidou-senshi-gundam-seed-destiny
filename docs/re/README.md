# Reverse-engineering notes

One file per subsystem. Mark every finding with how far it is proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely. Promote it to verified before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| text.md | encoding, control codes, pointer tables, renderer, kerning, archive, Le LZ | verified (identity/marker builds, extraction roundtrip) |
| graphics.md | survey of every graphics text site and how each is rebuilt | verified in-game except CHALLENGE missions 2-10 |
