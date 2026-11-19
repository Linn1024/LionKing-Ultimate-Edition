"""Actual dry output filtering for each independent menu source after flag fix."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_menu_output84_isolation.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-menu-output83'","ROOT/'build/pride-menu-enable86'")
source=source.replace("ROOT/'build/pride-menu-output84-isolation'","ROOT/'build/pride-menu-enable86-isolation'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
