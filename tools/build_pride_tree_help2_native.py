"""Compile the same paged helper and corrected virtual-device test for native SDL."""
from pathlib import Path

first_builder=Path(__file__).with_name('build_pride_tree_help_native.py')
source=first_builder.read_text().replace("ROOT/'build/pride-tree-help'","ROOT/'build/pride-tree-help2'")
source=source.replace(".as_posix()+'\"')", """.as_posix()+'"').replace('#include "tlk_resource_editor_selftest.h"','#include "'+(parent/'patched/tlk_resource_editor_selftest.h').as_posix()+'"')""")
source=source.replace('paths=[Path(__file__),original_builder,',"paths=[Path(__file__),first_builder,original_builder,parent/'patched/tlk_resource_editor_selftest.h',")
exec(compile(source,str(first_builder),'exec'))
