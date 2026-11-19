"""Actual published shortcut through default imported data and completed route."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_cmd53.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-checkpoint-capability53'","ROOT/'build/pride-menu-enable86'")
source=source.replace("ROOT/'dist/installed-preview53/package-report.json'","ROOT/'dist/installed-preview86/package-report.json'")
source=source.replace("base/'completion/report.json'","base/'route/report.json'")
source=source.replace("source.parent/'aot'","source.parent/'menus-aot'")
source=source.replace("prior['commands']['aot']","prior['commands']['menus-aot']")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
