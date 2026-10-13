import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / 'rom/1801 - Kidou Senshi Gundam Seed Destiny (J)(Caravan).gba'
SHA1 = '64eea52cd909669a972c091869c5f47865863bc0'


def test_original_rom_hash():
    assert hashlib.sha1(ORIG.read_bytes()).hexdigest() == SHA1
