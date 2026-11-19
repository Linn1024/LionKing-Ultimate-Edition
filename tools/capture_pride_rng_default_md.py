"""Observe ordinary MD default revival without a collected checkpoint."""
from pathlib import Path

original_verifier=Path(__file__).with_name('capture_pride_rng_md.py')
source=original_verifier.read_text().replace("base/'md'","base/'md-default'")
source=source.replace("(('completion',6000),('checkpoint',5400),('continue',16000))", "(('default',3600),)")
source=source.replace('field<=4000','field<=1400')
source=source.replace("name=='checkpoint' or field<=5400", "name=='default' or field<=5400")
source=source.replace('paths=[Path(__file__),source]','paths=[Path(__file__),original_verifier,source]')
exec(compile(source,str(original_verifier),'exec'))
