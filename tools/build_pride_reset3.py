"""Build reset with surviving effective audio choices and fresh machine state."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_reset.py')
source=original_builder.read_text().replace('build/pride-reset/fixed', 'build/pride-reset/fixed3')
source=source.replace('paths=[Path(__file__),', 'paths=[Path(__file__),original_builder,')
exec(compile(source,str(original_builder),'exec'))
