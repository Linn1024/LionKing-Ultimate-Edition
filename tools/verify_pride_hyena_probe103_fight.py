"""Current production103 against ordinary Normal fight; actual scoped probe calls."""
from pathlib import Path
verifier_source=Path(__file__).with_name('observe_pride_hyena_probe102_fight.py')
source=verifier_source.read_text().replace('pride-hyena-probe102-fight','pride-hyena-probe103-fight').replace("ROOT/'build/pride-hyena-probe101/player.exe'","ROOT/'build/pride-hyena-probe103/player.exe'")
source=source.replace('read_only_wrapper=True','ordinary_inputs=True')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
