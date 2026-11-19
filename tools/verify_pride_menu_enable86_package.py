"""Current installed package, original prepared data and ordinary completed route."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_menu_output83_package.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-menu-output83'","ROOT/'build/pride-menu-enable86'")
source=source.replace("ROOT/'dist/installed-preview83/package-report.json'","ROOT/'dist/installed-preview86/package-report.json'")
exec(compile(source,str(verifier_source),'exec'))
