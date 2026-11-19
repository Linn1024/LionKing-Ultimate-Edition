"""Extend reviewed scene dispatch to pristine pre-Pride menu contexts."""
from pathlib import Path

third_builder=Path(__file__).with_name('build_pride_launch3.py')
code=third_builder.read_text()
needle="exec(compile(source,str(first_builder),'exec'))"
assert code.count(needle)==1
extra="""source=source.replace("ROOT/'build/pride-launch3'","ROOT/'build/pride-launch4'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),third_builder,ROOT/\"engine/runner/tlk_pride_save_cold.inc\",')
source=source.replace('for p in (Path(__file__),','for p in (Path(__file__),third_builder,ROOT/\"engine/runner/tlk_pride_save_cold.inc\",')
expression="(ROOT/'engine/runner/tlk_pride_save_dispatch.inc').read_text()"
assert source.count(expression)==1
source=source.replace(expression,expression+".replace('static int PridePracticeSave(', 'static int PrideScenePracticeSave(')+(ROOT/'engine/runner/tlk_pride_save_cold.inc').read_text()")
"""
code=code.replace(needle,extra+needle)
exec(compile(code,str(third_builder),'exec'))
