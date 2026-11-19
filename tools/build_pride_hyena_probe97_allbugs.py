"""Read-only observer;323 linked inputs, actual current97 host object."""
from pathlib import Path
verifier_source=Path(__file__).with_name('build_pride_checkpoint52_allbugs.py')
source=verifier_source.read_text().replace('pride-checkpoint-animation52','pride-hyena-probe97')
source=source.replace('unchanged == 321 and len(all_inputs) == 322','unchanged == 322 and len(all_inputs) == 323')
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
