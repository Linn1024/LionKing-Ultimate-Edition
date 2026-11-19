"""Qualify practical Hakuna/Destiny delivery with explicit native AI/effects limits."""
import json
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/later917-qualified';out.mkdir(exist_ok=True)
names=['be-prepared867-sampler','be-prepared868-choices','be-prepared869-windows','later884-prepared','later885-choices','later886-windows','return888-background','return890-sampler','return891-choices','return892-windows','later899-audio','later904-fallback','later905-death','later911-bounds-data','later912-contacts','later916-setup']
paths=[ROOT/'build'/n/'report.json' for n in names];reports={n:bound(p) for n,p in zip(names,paths)}
build=ROOT/'build/later910/build-report.json';scene=ROOT/'build/hakuna787-helper/build-report.json';sprite=ROOT/'build/later909-helper/build-report.json'
for p in (build,scene,sprite):bound(p)
route=bound(ROOT/'build/later902-selected/report.json'); contacts=bound(ROOT/'build/later913-selected/report.json'); detour=bound(ROOT/'build/later914-combat/report.json')
checks={n:r['result']=='PASS' for n,r in reports.items()}
checks['native_contact_resource_walkthrough']=route['result']=='PASS'
checks['md_contact_be_prepared_walkthrough']=contacts['checks']['completed_be_prepared']
checks['md_contact_ordinary_return_combat']=all(detour['checks'].values())
checks['current_player_hash']=digest(build.parent/'player.exe')==json.loads(build.read_text())['binary_sha256']
scope="Practical Be Prepared and Simba's Return: per-scene verified MD backgrounds, reviewed adult Simba/hyena and owned prop artwork and independent palettes, adult HUD, separate level/death music with native music isolation, independent adult-hyena attack13/reaction4 voices. Selectable MD adult-hyena contact boxes cover84 reviewed poses (75 differ, up to20px); ambiguous/unmapped poses retain native bounds/art. Most AI/timing, RAM-generated lava and unreviewed actors/effects/death movement remain native. Both levels complete with new resources and native contacts; MD contacts complete Be Prepared and ordinary Return combat, but the old recorded Return route gets stuck and is not a full MD-contact walkthrough. Health5/delay200 agree in both originals. Pride Rock scenery/actors and bonus resource coverage remain pending, using explicit native fallback; final ending is not yet verified. Existing earlier resource packages/settings preserved."
paths += [Path(__file__),build,scene,sprite,ROOT/'build/later902-selected/report.json',ROOT/'build/later913-selected/report.json',ROOT/'build/later914-combat/report.json',ROOT/'Play Be Prepared MD.cmd',ROOT/'Play Simbas Return MD.cmd',ROOT/'profiles/be-prepared-md.ini',ROOT/'profiles/return-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope=scope,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
