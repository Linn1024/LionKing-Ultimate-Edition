"""Second renderer build: suppress the caption's original OAM slots explicitly."""
from pathlib import Path
template345=Path(__file__).with_name('build_level_caption343.py')
source=template345.read_text().replace('level-caption343','level-caption345')
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template345,bp,')
exec(compile(source,str(template345),'exec'))
