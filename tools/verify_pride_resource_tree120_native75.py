"""Current118 native75 gate after semantic resource-parent repair."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_hyena_probe103_native75.py')
source=verifier_source.read_text().replace('pride-hyena-probe103','pride-resource-tree118')
exec(compile(source,str(verifier_source),'exec'))
