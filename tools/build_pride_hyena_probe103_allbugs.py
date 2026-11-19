"""Current103 read-only tracked-field observer."""
from pathlib import Path
verifier_source=Path(__file__).with_name('build_pride_hyena_probe97_allbugs.py')
source=verifier_source.read_text().replace('pride-hyena-probe97','pride-hyena-probe103')
exec(compile(source,str(verifier_source),'exec'))
