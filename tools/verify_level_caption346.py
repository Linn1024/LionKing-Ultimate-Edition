"""Recheck the corrected caption client after the OAM suppression fix."""
from pathlib import Path
template346=Path(__file__).with_name('verify_level_caption344.py')
source=template346.read_text().replace('level-caption343','level-caption345').replace('level-caption344','level-caption346')
source=source.replace('paths=[Path(__file__),build,','paths=[Path(__file__),template346,build,')
exec(compile(source,str(template346),'exec'))
