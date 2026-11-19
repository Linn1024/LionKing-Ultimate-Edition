"""Full guest-state source neutrality after the effects-enable correction."""
from pathlib import Path
verifier_source=Path(__file__).with_name('audit_pride_menu_output83_regression.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-menu-output83/route/report.json'","ROOT/'build/pride-menu-enable86/route/report.json'")
source=source.replace("ROOT/'build/pride-menu-output84-isolation/report.json'","ROOT/'build/pride-menu-enable86-isolation/report.json'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
