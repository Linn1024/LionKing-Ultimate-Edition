"""Build prepared second-level foreground and dynamic scenery palette support."""
from pathlib import Path
template372=Path(__file__).with_name('build_cant_wait362.py')
source=template372.read_text().replace("base=ROOT/'build/hyena-hud356'","base=ROOT/'build/cant-wait362'")
source=source.replace('cant-wait362','cant-wait372',1) if False else source
source=source.replace("out=ROOT/'build/cant-wait362'","out=ROOT/'build/cant-wait372'")
start=source.index('rows=json.loads');end=source.index('\nfor label,template,src in tasks:',start)
source=source[:start]+"tasks=[('wide',b['compiles']['wide'],None),('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('assets',b['compiles']['assets'],ROOT/'engine/runner/tlk_md_assets.c')]"+source[end:]
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),template372,bp,')
source=source.replace('Live Cant Wait plane-B bands and owned palette fade; native foreground retained. TLKVIEW history4 carries small pointer-free camera/palette state; cache-v1 unchanged.','Cant Wait prepared MD foreground mappings and dynamic foreground/background palette. Only validated cells substitute; actual native collisions unchanged. Existing scene cache format with richer prepared scene1 data.')
exec(compile(source,str(template372),'exec'))
