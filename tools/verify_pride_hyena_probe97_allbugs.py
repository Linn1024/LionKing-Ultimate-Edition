"""Full original tracked-field gate for current native walking-probe build."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint52_allbugs.py')
source=verifier_source.read_text().replace('pride-checkpoint-animation52','pride-hyena-probe97')
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
