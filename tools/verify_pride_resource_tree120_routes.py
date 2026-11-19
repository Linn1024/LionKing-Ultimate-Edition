"""Current118 complete native/MD walking-probe source and mode routes."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_hyena_probe99_routes.py')
source=verifier_source.read_text().replace('pride-hyena-probe97','pride-resource-tree118')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
