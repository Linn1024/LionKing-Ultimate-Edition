"""Build a fresh mixed frontend with the plain-SDL resource tree."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_singlepass.py')
source=original_builder.read_text()
source=source.replace("ROOT/'build/pride-singlepass'","ROOT/'build/pride-soft-tree'")
source=source.replace("ROOT/'tools/pride_singlepass_present_probe.c'","ROOT/'tools/pride_soft_tree_present_probe.c'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_builder,')
exec(compile(source,str(original_builder),'exec'))
