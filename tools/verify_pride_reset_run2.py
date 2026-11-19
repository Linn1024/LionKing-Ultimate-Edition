"""Retain the complete reset comparisons for the corrected timing shadows."""
from pathlib import Path

original = Path(__file__).with_name('verify_pride_reset_run.py')
source = original.read_text().replace('build/pride-reset/views', 'build/pride-reset/views2')
source = source.replace('paths=(Path(__file__),', 'paths=(Path(__file__),Path(original),')
exec(compile(source, str(original), 'exec'))
