"""Build native scene-v2 preparer with installed terrain contact tables."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait371_helper.py')
source=template.read_text().replace('cant-wait371-cmake','pride378-cmake')
source=source.replace("paths=[Path(__file__),", "paths=[Path(__file__),template,ROOT/'engine/runner/tlk_contact_map.c',ROOT/'engine/runner/tlk_contact_map.h',ROOT/'engine/runner/tlk_md_assets_cache.inc',")
exec(compile(source,str(template),'exec'))
