"""Published real windows; run only after the actual CMD check completes."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_checkpoint_public_window53.py')
source=original.read_text().replace("ROOT/'build/pride-checkpoint-capability53'","ROOT/'build/pride-menu-output83'")
source=source.replace("ROOT/'dist/installed-preview53/package-report.json'","ROOT/'dist/installed-preview83/package-report.json'")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),original,')
exec(compile(source,str(original),'exec'))
