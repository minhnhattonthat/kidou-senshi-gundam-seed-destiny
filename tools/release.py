"""Local release: build -> check -> smoke -> leftover-Japanese scan -> BPS (made + re-applied) -> README -> zip.
Stops at the first failure. Never uploads anything.

    python -X utf8 tools/release.py [--version 0.1]
"""
import argparse
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / '.agents/skills/translate-retro-game/scripts'
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

KNOWN_ISSUES = [
    'CHALLENGE MODE: only mission 1 of the pause-screen mission text was checked in-game; later missions use the '
    'same English fragments but their layout was not verified.',
    'The title logo was redrawn by script (GUNDAM / MOBILE SUIT); faint traces of the old art may remain.',
    'The embedded bonus game "MS Gundam SEED Battle Assault" was already in English and is unchanged.',
]


def run(cmd, what):
    print('==', what)
    res = subprocess.run(cmd, cwd=ROOT)
    if res.returncode:
        raise SystemExit('%s failed (exit %d)' % (what, res.returncode))


def hashes(data):
    return {'CRC32': '%08X' % zlib.crc32(data), 'MD5': hashlib.md5(data).hexdigest(),
            'SHA-1': hashlib.sha1(data).hexdigest()}


def readme(version, orig, built):
    o, b = hashes(orig), hashes(built)
    lines = [
        'Mobile Suit Gundam SEED Destiny (GBA) - English translation patch v%s' % version, '',
        'Unofficial fan translation. No ROMs are distributed; you need your own dump.', '',
        'Apply the BPS patch (Floating IPS, beat or RomPatcher.js) to:',
        '  1801 - Kidou Senshi Gundam Seed Destiny (J)(Caravan).gba  (Kidou Senshi Gundam SEED Destiny, Japan)',
        '  size %d bytes' % len(orig)] + ['  %-6s %s' % kv for kv in o.items()] + [
        '', 'Patched result: size %d bytes' % len(built)] + ['  %-6s %s' % kv for kv in b.items()] + [
        '', 'What is translated:',
        '  - all dialogue: shop keepers, unlock messages, win quotes for every pilot, new game / link messages',
        '    (new proportional font)',
        '  - pilot and mobile suit name plates, stage names, shop item names, main-menu mode descriptions',
        '  - title logo and copyright line, CHALLENGE MODE mission text',
        '', 'Names follow the official English spellings (Shinn Asuka, Athrun Zala, Lunamaria Hawke, Saviour...).',
        '', 'Tested in Mesen 2 (GBA, with a real BIOS). Start from a cold boot, not from an old savestate.',
        'Saves (EEPROM) from the Japanese game keep working.', '',
        'Known issues:'] + ['  - ' + k for k in KNOWN_ISSUES] + [
        '', 'Credits: translation, hacking and tools by the project team, with AI assistance (Claude).',
        'Mobile Suit Gundam SEED Destiny (c) Sotsu Agency, Sunrise, MBS. Game (c) Bandai 2004.', '']
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', default='0.1')
    a = ap.parse_args()
    py = [sys.executable, '-X', 'utf8']
    run(py + ['tools/check.py'], 'check (tests + lint)')
    run(py + ['build.py', 'english'], 'build')
    built_path = ROOT / 'build/gsd_en.gba'
    run(py + [str(SKILL / 'emu.py'), str(built_path), '--out', 'work/qa/release_smoke', '--route',
              'tools/routes/boot.txt', '--smoke', '--timeout', '200'], 'smoke')
    lo, hi = build.tm.REGION  # skip asm/main.asm code at build.CODE (its bytes decode as kana)
    run(py + [str(SKILL / 'jp_left.py'), str(built_path), '--tbl', 'tbl/jp.tbl', '--range',
              '%X-%X' % (lo, build.CODE), '--range', '%X-%X' % (build.CODE + 0x100, hi)],
        'leftover Japanese in the script region')
    out = ROOT / 'release'
    out.mkdir(exist_ok=True)
    name = 'Gundam_SEED_Destiny_GBA_EN_v%s' % a.version
    patch = out / (name + '.bps')
    run(py + [str(SKILL / 'bps.py'), 'make', str(build.tm.ORIG), str(built_path), str(patch)], 'bps make + verify')
    text = readme(a.version, build.tm.rom(), built_path.read_bytes())
    (out / 'README.txt').write_text(text, encoding='utf-8', newline='\r\n')
    with zipfile.ZipFile(out / (name + '.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / 'README.txt', 'README.txt')
    print('release ready:', out / (name + '.zip'))


if __name__ == '__main__':
    main()
