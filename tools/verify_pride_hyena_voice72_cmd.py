"""Actual public CMD and default installed data after hyena voice publication."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_cmd53.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-checkpoint-capability53'","ROOT/'build/pride-hyena-voice72'")
source=source.replace("ROOT/'dist/installed-preview53/package-report.json'","ROOT/'dist/installed-preview72/package-report.json'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
