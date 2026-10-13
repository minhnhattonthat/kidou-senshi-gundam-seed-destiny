# Glossary - Kidou Senshi Gundam SEED Destiny (GBA)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
The lint (`tools/lint.py`) enforces the tables: if the JP term appears in a line, the EN form must appear too, and
nothing in the Avoid column may appear.

## Rulings (user, 2026-10-13)
- Names: official English (Bandai) spellings, Western order, no honorifics (-san etc. dropped or rendered by tone).
- Credits: English. Full names and terms; prefer engine work to abbreviation; abbreviate only as a flagged last resort.
- All graphics text in scope.
- Register: anime-faithful voices (Kira earnest, Shinn hot-headed, Lacus gentle and polite, Cagalli blunt and
  boyish, Azrael smarmy "heh heh heh", Orga/Clotho/Shani feral, Rau theatrical).
- Mode/menu names stay in the game's own English caps: MAIN MODE, VS MODE, TRAINING MODE, SURVIVAL MODE,
  CHALLENGE MODE, TIME TRIAL MODE, FREE BATTLE MODE, OPTIONS, SHOP, MS SELECT, STAGE SELECT, COM LEVEL,
  VERY HARD, HARD, POINT(S).

## Style rules
- Punctuation: 「」 -> "...", ・・・ -> ..., ！！ -> !!, ！？ -> ?!, ～ -> ~, 、 -> ,
- `{num}` (a number) must start a line: "{n}{num} POINTS obtained!" (text runs start on 16 px cells).
- Keep every control token the JP has ({f5:..}, {f6:..}, {key}, {fb:..}, {f4:..}, {num}); {n}/{page} may move.
  Keep the "{page}{n}{n}" shape after a page break and the leading "{n}".
- Shop box: 2 lines per page, 224 px per line, 208 px for a line followed by {key}/{page}. Win quotes: 3 lines per
  page, same widths. Check with `python -X utf8 tools/lint.py --fit shop "..."`.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| キラ・ヤマト | Kira Yamato | | | |
| アスラン | Athrun | | | Asuran |
| ラクス | Lacus | | Lacus Clyne | Rakusu |
| カガリ | Cagalli | | Cagalli Yula Athha | Kagari |
| ムウ | Mu | | Mu La Flaga | Mwu, Muu |
| イザーク・ジュール | Yzak Joule | | | Yzak Jule |
| ディアッカ | Dearka | | Dearka Elsman | |
| ニコル | Nicol | | Nicol Amalfi | |
| クルーゼ | Creuset | | Rau Le Creuset | |
| シン・アスカ | Shinn Asuka | | (JP key is the full name: マシン contains シン) | Shin |
| マユ | Mayu | | Shinn's sister | |
| ルナマリア | Lunamaria | | Lunamaria Hawke | |
| レイ・ザ・バレル | Rey Za Burrel | | | Rey Za Barrel |
| ステラ | Stella | | Stella Loussier | Stellar |
| スティング | Sting | | Sting Oakley | |
| アウル | Auel | | Auel Neider | |
| アズラエル | Azrael | | Muruta Azrael | |
| オルガ | Orga | | Orga Sabnak | |
| クロト | Clotho | | Clotho Buer | |
| シャニ | Shani | | Shani Andras | |
| ロウ | Lowe | | Lowe Guele | |
| ミナ | Mina | | Rondo Mina Sahaku | |
| タリア・グラディス | Talia Gladys | | | |
| ハロ | Haro | | | |

## Mobile suits, ships, places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ストライク | Strike | | | |
| イージス | Aegis | | | |
| バスター | Buster | | | |
| レイダー | Raider | | | |
| カラミティ | Calamity | | | |
| フォビドゥン | Forbidden | | | |
| デュエル | Duel | | | |
| ブリッツ | Blitz | | | |
| シグー | CGUE | | | Cigue |
| アストレイ | Astray | | | |
| フリーダム | Freedom | | | |
| ジャスティス | Justice | | | |
| フォースインパルス | Force Impulse | | | |
| ソードインパルス | Sword Impulse | | | |
| ブラストインパルス | Blast Impulse | | | |
| カオス | Chaos | | | |
| ガイア | Gaia | | | |
| アビス | Abyss | | | |
| セイバー | Saviour | | | Saber, Savior |
| スラッシュザクファントム | Slash ZAKU Phantom | | | Zaku |
| ブレイズザクファントム | Blaze ZAKU Phantom | | | Zaku |
| ガナーザクウォーリア | Gunner ZAKU Warrior | | | Zaku |
| ザクウォーリア | ZAKU Warrior | | | Zaku |
| プロヴィデンス | Providence | | | |
| ゴールドフレーム | Gold Frame Amatsu Mina | | official: Astray Gold Frame Amatsu Mina | |
| アークエンジェル | Archangel | | | |
| アメノミハシラ | Ame-no-Mihashira | | | |
| ミラージュコロイド | Mirage Colloid | | | |

## Game terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ステージセレクト | STAGE SELECT | | screen name | |
| サバイバルモード | SURVIVAL MODE | | | |
| タイムトライアルモード | TIME TRIAL MODE | | | |
| 衣装 | outfit | | Lacus changes outfits | costume |

## Decisions from earlier batches
- (none yet)
