"""Build the MMIO reset correction while retaining the first failed candidate."""
from pathlib import Path

original = Path(__file__).with_name('build_pride_reset.py')
source = original.read_text().replace('build/pride-reset/fixed', 'build/pride-reset/fixed2')
source = source.replace('paths=[Path(__file__),', 'paths=[Path(__file__),Path(original),')
exec(compile(source, str(original), 'exec'))
