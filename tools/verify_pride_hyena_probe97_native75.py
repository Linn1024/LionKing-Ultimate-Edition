"""Current native75 endpoint gate for independent walking probe availability."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_menu_enable86_native75.py')
source=verifier_source.read_text().replace('pride-menu-enable86','pride-hyena-probe97')
exec(compile(source,str(verifier_source),'exec'))
