"""Current maintained menu integration through the full native75 endpoint set."""
from pathlib import Path
template237=Path(__file__).with_name('verify_pride_hyena_entrance142_native75.py')
source=template237.read_text().replace('pride-hyena-entrance139','pride-menu226-integrated')
source=source.replace("'max_workers=12'","'max_workers=6'")
source=source.replace('paths = [Path(__file__),verifier_source,build_path,','paths = [Path(__file__),template237,verifier_source,build_path,')
exec(compile(source,str(template237),'exec'))
