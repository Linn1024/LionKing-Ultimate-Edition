"""Stage current accepted-menu-tail correction; public74 remains unchanged."""
from pathlib import Path
verifier_source=Path(__file__).with_name('package_pride_menu_output83.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-menu-output83'","ROOT/'build/pride-menu-enable86'")
source=source.replace("ROOT/'dist/installed-preview83'","ROOT/'dist/installed-preview86'")
source=source.replace("('route','resume','windows-ui')","('route','enable','windows-ui')")
source=source.replace("'pride-menu-output83-owner-component'","'pride-menu-enable86-owner-component'")
source=source.replace("'pride-menu-output84-isolation'","'pride-menu-enable86-isolation'")
source=source.replace('preview83','preview86').replace('installed-preview83','installed-preview86')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
