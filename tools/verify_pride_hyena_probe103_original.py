"""Current103 adapter in the original walking decisions; previous98 retained."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_hyena_probe98.py')
source=verifier_source.read_text().replace("out=ROOT/'build/pride-hyena-probe98'","out=ROOT/'build/pride-hyena-probe103-original'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
