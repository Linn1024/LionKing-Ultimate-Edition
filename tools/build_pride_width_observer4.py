"""Keep read-only route snapshots with the boss-save eligibility correction."""
from pathlib import Path

third_builder=Path(__file__).with_name('build_pride_width_observer3.py')
source=third_builder.read_text().replace('build/pride-rng-player3','build/pride-rng-player4')
source=source.replace("'paths=[Path(__file__),original_builder,width_builder,bp,",
                      "'paths=[Path(__file__),original_builder,width_builder,third_builder,bp,")
exec(compile(source,str(third_builder),'exec'))
