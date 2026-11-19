"""Use current86 completed-route settings; retain the failed legacy-path attempt."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_public_window53.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-checkpoint-capability53'","ROOT/'build/pride-menu-enable86'")
source=source.replace("ROOT/'dist/installed-preview53/package-report.json'","ROOT/'dist/installed-preview86/package-report.json'")
source=source.replace("out = base/'game-window-verification'","out = base/'game-window-verification2'")
source=source.replace("base/'completion/aot'/before","base/'route/menus-aot'/before")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
