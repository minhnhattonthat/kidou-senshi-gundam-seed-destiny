import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import lint  # noqa: E402


def test_every_translated_line_passes_lint():
    terms = lint.glossary_terms()
    bad = {r['id']: lint.lint_row(r, terms) for r in lint.all_rows() if r['en']}
    assert not {k: v for k, v in bad.items() if v}


def test_lint_catches_overflow_and_codes():
    row = {'id': '0C9530_013', 'jp': '{n}何と交換いたしますか？{end}', 'en': '{n}' + 'W' * 40 + '{key}{end}'}
    errs = lint.lint_row(row)
    assert any('px' in e for e in errs) and any('control codes' in e for e in errs)
