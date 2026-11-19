"""Current226 ordinary mixed completion, with independent entrance selection."""
from pathlib import Path
template252=Path(__file__).with_name('verify_pride_hyena_entrance148_routes.py')
source=template252.read_text().replace('pride-hyena-entrance139','pride-menu226-integrated').replace('routes148','routes252')
source=source.replace("'paths=[Path(__file__),verifier_source,'", "'paths=[Path(__file__),template252,verifier_source,'")
exec(compile(source,str(template252),'exec'))
