"""Current118 full original tracked-field All Bugs verification."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint52_allbugs.py')
source=verifier_source.read_text().replace('pride-checkpoint-animation52','pride-resource-tree118')
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
