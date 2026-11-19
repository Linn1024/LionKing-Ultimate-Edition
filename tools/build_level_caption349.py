"""Handle the native second line entering upward as well as letters falling."""
from pathlib import Path
template349=Path(__file__).with_name('build_level_caption343.py')
source=template349.read_text().replace('level-caption343','level-caption349')
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template349,bp,')
exec(compile(source,str(template349),'exec'))
