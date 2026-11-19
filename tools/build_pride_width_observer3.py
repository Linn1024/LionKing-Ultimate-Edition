"""Retain read-only route snapshots around candidate3's distinct temporary files."""
from pathlib import Path

width_builder=Path(__file__).with_name('build_pride_width_observer.py')
source=width_builder.read_text()
source=source.replace('source=original_builder.read_text()',
    'source=original_builder.read_text().replace("parent=ROOT/\'build/pride-rng-player2\'", "parent=ROOT/\'build/pride-rng-player3\'")')
source=source.replace("'paths=[Path(__file__),original_builder,bp,", "'paths=[Path(__file__),original_builder,width_builder,bp,")
exec(compile(source,str(width_builder),'exec'))
