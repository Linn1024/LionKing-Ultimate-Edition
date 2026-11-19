"""Verify virtual editor devices after SDL's preceding Guide press is released."""
from pathlib import Path

first_verifier=Path(__file__).with_name('verify_pride_tree_help_remap.py')
source=first_verifier.read_text().replace("ROOT/'build/pride-tree-help'","ROOT/'build/pride-tree-help2'")
source=source.replace('paths=[Path(__file__),original_verifier]','paths=[Path(__file__),first_verifier,original_verifier]')
exec(compile(source,str(first_verifier),'exec'))
