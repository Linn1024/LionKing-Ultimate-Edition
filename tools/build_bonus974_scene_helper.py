"""Prepare scene-v3 with full Hakuna streamed names and waterfall images."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait371_helper.py')
s=template.read_text().replace('cant-wait371-cmake','bonus974-scene-helper')
s=s.replace("paths=[Path(__file__),", "paths=[Path(__file__),template,ROOT/'engine/runner/tlk_md_assets_cache.inc',ROOT/'engine/runner/tlk_md_assets.h',")
exec(compile(s,str(template),'exec'))
