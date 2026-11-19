"""Build ordinary native canvas using the same staged resource-help header."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_singlepass_native.py')
source=original_builder.read_text()
source=source.replace("ROOT/'build/pride-singlepass'","ROOT/'build/pride-tree-help'")
source=source.replace("ROOT/'tools/pride_singlepass_present_probe.c'","ROOT/'tools/pride_tree_help_present_probe.c'")
source=source.replace('source=patched.read_text()', '''source=patched.read_text().replace('#include "tlk_resource_editor_sdl.h"','#include "'+(parent/'patched/tlk_resource_editor_sdl.h').as_posix()+'"')''')
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_builder,parent/'patched/tlk_resource_editor_sdl.h',ROOT/'engine/runner/tlk_resource_editor_selftest.h',")
exec(compile(source,str(original_builder),'exec'))
