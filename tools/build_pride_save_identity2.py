"""Retain the initial candidate and bind component order in compatibility schema2."""
from pathlib import Path

first_builder=Path(__file__).with_name('build_pride_save_identity.py')
source=first_builder.read_text().replace('from pride_save_identity import','from pride_save_identity2 import')
source=source.replace("ROOT/'build/pride-save-identity'","ROOT/'build/pride-save-identity2'")
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),first_builder,ROOT/'tools/pride_save_identity2.py',")
exec(compile(source,str(first_builder),'exec'))
