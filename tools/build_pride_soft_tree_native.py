"""Build the ordinary native sibling of the fallback-tree candidate."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_singlepass_native.py')
source=original_builder.read_text()
source=source.replace("ROOT/'build/pride-singlepass'","ROOT/'build/pride-soft-tree'")
source=source.replace("ROOT/'tools/pride_singlepass_present_probe.c'","ROOT/'tools/pride_soft_tree_present_probe.c'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_builder,ROOT/\'engine/runner/tlk_resource_editor_sdl.h\',')
exec(compile(source,str(original_builder),'exec'))
