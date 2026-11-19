"""Repeat only the held skull encounter with the independent original MD walking query."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard664_skull_middle.py')
s=template.read_text().replace("exec(compile(s,str(template),'exec'))", "s=s.replace('build/graveyard659/build-report.json','build/graveyard665/build-report.json').replace('build/graveyard664-skull-middle','build/graveyard666-md-probe')\ns=s.replace(\"TLK_GRAVEYARD_ACTOR_TRACE=str(folder/'actors.csv'),\",\"TLK_GRAVEYARD_ACTOR_TRACE=str(folder/'actors.csv'),TLK_HYENA_PROBE_TRACE=str(folder/'probe.csv'),\")\nexec(compile(s,str(template),'exec'))")
exec(compile(s,str(template),'exec'))
