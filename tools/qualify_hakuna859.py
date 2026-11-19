"""Qualify practical Hakuna/Destiny delivery with explicit native AI/effects limits."""
import json
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna859-qualified';out.mkdir(exist_ok=True)
names=['hakuna788-prepared','hakuna789-player','hakuna791-windows','hakuna816-actors','hakuna817-opening','destiny818-route','hakuna825-prepared','hakuna826-actors','hakuna830-hud','hakuna831-hud','hakuna846-music','hakuna847-tokens','hakuna853-roar','hakuna854-death','hakuna858-setup']
paths=[ROOT/'build'/n/'report.json' for n in names];reports={n:bound(p) for n,p in zip(names,paths)}
build=ROOT/'build/hakuna849/build-report.json';scene=ROOT/'build/hakuna787-helper/build-report.json';sprite=ROOT/'build/hakuna822-helper/build-report.json'
for p in (build,scene,sprite):bound(p)
route=bound(ROOT/'build/hakuna856-selected/report.json')
checks={n:r['result']=='PASS' for n,r in reports.items()}
checks['final_selected_route_healthy']=route['checks']['healthy_destiny']
checks['current_player_hash']=digest(build.parent/'player.exe')==json.loads(build.read_text())['binary_sha256']
scope='Practical mixed Hakuna/Destiny resources: verified scene-v3 backgrounds, reviewed cub/adult/gorilla and later-actor art/colors, common HUD including adult portrait, separate level/death music with native-music isolation, Hakuna shared cub roar/hurt/roll/bounce, selectable cub death movement/roar and normal gorilla recovery11. Native other AI/timing, unknown/flashing art, stage-owned enemy effects, adult effects/death movement, fall/final-life paths and unsupported scene presentation remain explicit. Full native-gameplay Destiny route reaches Be Prepared. Final selected gorilla route reaches healthy Destiny; it does not visit normal recovery, separately exercised847/850/853. Bonus13 entry/return observed, resource audit still pending. No universal MD parity claim.'
paths += [Path(__file__),build,scene,sprite,ROOT/'build/hakuna856-selected/report.json',ROOT/'tools/capture_hakuna854_death.py',ROOT/'Play Hakuna Matata MD.cmd',ROOT/'Play Simbas Destiny MD.cmd',ROOT/'profiles/hakuna-md.ini',ROOT/'profiles/destiny-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope=scope,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
