"""Stage complete paged resource help and virtual-device editor checks."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_singlepass.py')
source=original_builder.read_text()
source=source.replace("ROOT/'build/pride-singlepass'","ROOT/'build/pride-tree-help'")
source=source.replace("ROOT/'tools/pride_singlepass_present_probe.c'","ROOT/'tools/pride_tree_help_present_probe.c'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_builder,')
exec(compile(source,str(original_builder),'exec'))
