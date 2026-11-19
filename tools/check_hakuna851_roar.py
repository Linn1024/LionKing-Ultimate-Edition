"""Correct the roar fixture's controller button; retain the qualified death/boss checks."""
import json
from pathlib import Path
template=Path(__file__).with_name('check_hakuna850_behavior.py');s=template.read_text();exec(compile(s[:s.index("fixture='build/")],str(template),'exec'))
out=ROOT/'build/hakuna851-roar';out.mkdir(exist_ok=True);cases={}
boss='build/hakuna803-gorilla/encounter.native.state'
run('native',boss,35060,35250,'',pad=0x80)
run('md',boss,35060,35250,'gameplay.simba.roar = md\naudio.effects.simba.roar = md\n',pad=0x80)
prior=json.loads((ROOT/'build/hakuna850-behavior/report.json').read_text());checks={k:v for k,v in prior['checks'].items() if k not in ('roar14','roar_voice')}
checks.update(roar14=any(r['event']=='activation_delay' and r['value']=='14' for r in cases['md']['roar']),roar_voice=any(r['selector']=='19' and r['value']=='10' for r in cases['md']['commands']),native_roar_untouched=not cases['native']['roar'])
paths=[Path(__file__),template,ROOT/'build/hakuna850-behavior/report.json',ROOT/'build/hakuna849/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
