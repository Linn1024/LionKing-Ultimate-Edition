"""All75 original native endpoints after accepted menu-tail filtering fix."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_menu_output83_native75.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-menu-output83'","ROOT/'build/pride-menu-enable86'")
exec(compile(source,str(verifier_source),'exec'))
