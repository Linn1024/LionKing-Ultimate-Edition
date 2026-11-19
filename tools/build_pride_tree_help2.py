"""Retain the first candidate and stage the SDL Guide-release test correction."""
from pathlib import Path

first_builder=Path(__file__).with_name('build_pride_tree_help.py')
source=first_builder.read_text().replace("ROOT/'build/pride-tree-help'","ROOT/'build/pride-tree-help2'")
source=source.replace('paths=[Path(__file__),original_builder,','paths=[Path(__file__),first_builder,original_builder,')
exec(compile(source,str(first_builder),'exec'))
