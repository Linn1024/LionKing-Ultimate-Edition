"""Locate ordinary opening captions earlier in the next two practice levels."""
from pathlib import Path
template341=Path(__file__).with_name('capture_level_caption340.py')
source=template341.read_text().replace('level-caption340','level-caption341').replace("='1800'","='1550'")
source=source.replace("source_sha256={Path(__file__)","source_sha256={Path(__file__)")
exec(compile(source,str(template341),'exec'))
