"""Templated shop lines (unlock notices / MS SELECT tips): one English pattern per voice, the suit name filled in.

    python -X utf8 tools/tl_templates.py > work/tl/templates.tsv   (key<TAB>english, for tlpairs.py merge)
Each pattern is tried in order until tools/lint.py accepts the line, so long suit names get a roomier layout.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import lint  # noqa: E402

MS = {'ストライク': 'Strike', 'イージス': 'Aegis', 'バスター': 'Buster', 'レイダー': 'Raider',
      'カラミティ': 'Calamity', 'フォビドゥン': 'Forbidden', 'デュエル': 'Duel', 'ブリッツ': 'Blitz',
      'シグー': 'CGUE', 'アストレイ': 'Astray', 'フリーダム': 'Freedom', 'ジャスティス': 'Justice',
      'フォースインパルス': 'Force Impulse', 'ソードインパルス': 'Sword Impulse',
      'ブラストインパルス': 'Blast Impulse', 'カオス': 'Chaos', 'ガイア': 'Gaia', 'アビス': 'Abyss',
      'セイバー': 'Saviour', 'スラッシュザクファントム': 'Slash ZAKU Phantom', 'プロヴィデンス': 'Providence',
      'ゴールドフレーム天ミナ': 'Gold Frame Amatsu Mina', 'ゴールドフレーム{sp8}アマツ{sp8}ミナ': 'Gold Frame Amatsu Mina',
      'ザクウォーリア': 'ZAKU Warrior', 'ブレイズザクファントム': 'Blaze ZAKU Phantom',
      'ガナーザクウォーリア': 'Gunner ZAKU Warrior'}
NAME = '「(?P<ms>[^」]+)」'
# (JP regex, [English patterns in preference order]); {ms} = suit name. Voices: Lacus polite (ます),
# Cagalli blunt (ぞ / んだ), Azrael smarmy (くっくっく).
FAMILIES = [
    (r'\{n\}MS\{sp8\}SELECTがめんで\{n\}' + NAME + r'に.*LRボタンで(\{n\})?選択できます。\{page\}\{n\}\{n\}また、このキャラで'
     r'CHALLENGE\{n\}MODEはプレイできません。\{key\}\{end\}',
     ['{n}On the MS SELECT screen, highlight{n}"{ms}" and press L or R{page}{n}{n}to select it.{page}{n}{n}'
      'Also, this character can\'t be{n}played in CHALLENGE MODE.{key}{end}',
      '{n}On the MS SELECT screen, highlight{n}"{ms}"{page}{n}{n}and press L or R to select it.{page}{n}{n}'
      'Also, this character can\'t be{n}played in CHALLENGE MODE.{key}{end}']),
    (r'\{n\}MS\{sp8\}SELECTがめんで\{n\}' + NAME + r'に.*LRボタンで(\{n\})?選択できるぞ。\{page\}\{n\}\{n\}また、このキャラで'
     r'CHALLENGE\{n\}MODEはプレイできないんだ。\{key\}(B621)?\{end\}',
     ['{n}Highlight "{ms}" on the{n}MS SELECT screen and hit L or R{page}{n}{n}to pick it.{page}{n}{n}'
      'But you can\'t play this character{n}in CHALLENGE MODE.{key}{end}',
      '{n}Highlight "{ms}"{n}on the MS SELECT screen{page}{n}{n}and hit L or R to pick it.{page}{n}{n}'
      'But you can\'t play this character{n}in CHALLENGE MODE.{key}{end}']),
    (r'\{n\}MS\{sp8\}SELECTがめんで\{n\}' + NAME + r'に.*LRボタンで(\{n\})?選択できます。\{key\}\{end\}',
     ['{n}On the MS SELECT screen, highlight{n}"{ms}" and press L or R{page}{n}{n}to select it.{key}{end}',
      '{n}On the MS SELECT screen, highlight{n}"{ms}"{page}{n}{n}and press L or R to select it.{key}{end}']),
    (r'\{n\}MS\{sp8\}SELECTがめんで\{n\}' + NAME + r'に.*LRボタンで(\{n\})?選択できるぞ。\{key\}\{end\}',
     ['{n}Highlight "{ms}" on the{n}MS SELECT screen and hit L or R{page}{n}{n}to pick it.{key}{end}',
      '{n}Highlight "{ms}"{n}on the MS SELECT screen{page}{n}{n}and hit L or R to pick it.{key}{end}']),
    (r'\{n\}MS\{sp8\}SELECTがめんに\{n\}' + NAME + r'が(\{page\}\{n\}\{n\})?ついか(\{page\}\{n\}\{n\})?されました。\{key\}\{end\}',
     ['{n}"{ms}" has been added{n}to the MS SELECT screen.{key}{end}',
      '{n}"{ms}"{n}has been added to the MS SELECT screen.{key}{end}',
      '{n}"{ms}"{n}has been added{page}{n}{n}to the MS SELECT screen.{key}{end}']),
    (r'\{n\}MS\{sp8\}SELECTがめんに\{n\}' + NAME + r'が(\{page\}\{n\}\{n\})?ついか(\{page\}\{n\}\{n\})?されました！\{end\}',
     ['{n}"{ms}" has been added{n}to the MS SELECT screen!{end}',
      '{n}"{ms}"{n}has been added to the MS SELECT screen!{end}',
      '{n}"{ms}"{n}has been added{page}{n}{n}to the MS SELECT screen!{end}']),
    (r'\{n\}MS\{sp8\}SELECTがめんに\{n\}' + NAME + r'が(\{page\}\{n\}\{n\})?ついか(\{page\}\{n\}\{n\})?されたぞ。\{key\}\{end\}',
     ['{n}"{ms}" is on the{n}MS SELECT screen now!{key}{end}',
      '{n}"{ms}"{n}is on the MS SELECT screen now!{key}{end}']),
    (r'\{n\}MS\{sp8\}SELECTがめんに\{n\}' + NAME + r'が・・\{page\}\{n\}\{n\}\{f4:01\}くっくっく・・・。\{key\}\{end\}',
     ['{n}"{ms}" has found its way{n}onto the MS SELECT screen...{page}{n}{n}{f4:01}Heh heh heh...{key}{end}',
      '{n}The MS SELECT screen now has{n}"{ms}"...{page}{n}{n}{f4:01}Heh heh heh...{key}{end}']),
]


def fill(rows):
    out = {}
    for row in rows:
        for rx, patterns in FAMILIES:
            m = re.fullmatch(rx, row['jp'])
            if not m:
                continue
            ms = MS[m['ms']]
            for pat in patterns:
                en = pat.replace('{ms}', ms)
                if not lint.lint_row(dict(row, en=en)):
                    out[row['id']] = en
                    break
            else:
                raise SystemExit('no pattern fits %s (%s)' % (row['id'], ms))
            break
    return out


if __name__ == '__main__':
    keys = [ln.split('\t')[0] for ln in (ROOT / 'work/tl/unique.tsv').read_text(encoding='utf-8').splitlines()]
    rows = {r['id']: r for r in lint.all_rows()}
    for k, en in fill(rows[k] for k in keys).items():
        print('%s\t%s' % (k, en))
