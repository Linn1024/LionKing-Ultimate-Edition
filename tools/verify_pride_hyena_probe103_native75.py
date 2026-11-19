"""Current103 complete native endpoint gate."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_hyena_probe97_native75.py')
source=verifier_source.read_text().replace('pride-hyena-probe97','pride-hyena-probe103')
exec(compile(source,str(verifier_source),'exec'))
