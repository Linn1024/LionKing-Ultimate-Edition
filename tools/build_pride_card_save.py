"""Carry a complete idle Pride context through the native level-card save."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_boss_save.py')
source=original_builder.read_text().replace("parent=ROOT/'build/pride-rng-player3'", "parent=ROOT/'build/pride-rng-player4'")
source=source.replace("out=ROOT/'build/pride-rng-player4'", "out=ROOT/'build/pride-rng-player5'")
source=source.replace("predicate=ROOT/'engine/runner/tlk_pride_play_scene.inc'", "predicate=ROOT/'engine/runner/tlk_pride_save_scene.inc'")
start=source.index("    anchor='static int practice_context_ready(void) {'")
end=source.index("    source=out/'host.i'",start)
source=source[:start]+'''    previous_predicate=ROOT/'engine/runner/tlk_pride_play_scene.inc'
    assert text.count(previous_predicate.read_text())==1
    text=text.replace(previous_predicate.read_text(),predicate.read_text())
    assert text.count('PrideOrdinaryPlayScene(')==1
    text=text.replace('PrideOrdinaryPlayScene(', 'PrideCompleteContextScene(')
'''+source[end:]
source=source.replace('paths=[Path(__file__),bp,original,source,predicate,',
                      'paths=[Path(__file__),original_builder,bp,original,source,predicate,previous_predicate,')
source=source.replace('Candidate4 boss-save eligibility built;', 'Candidate5 complete-cache card eligibility built;')
exec(compile(source,str(original_builder),'exec'))
