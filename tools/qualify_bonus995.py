"""Qualify practical bonus resources without claiming MD bonus gameplay or ending art."""
import json
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/bonus995-qualified';out.mkdir(exist_ok=True)
names=['bonus964-background','bonus970-prepared','bonus971-sampler','bonus972-choices','bonus990-audio','bonus991-play','bonus992-rounds','bonus994-setup']
paths=[ROOT/'build'/n/'report.json' for n in names];reports={n:bound(p) for n,p in zip(names,paths)};checks={n:r['result']=='PASS' for n,r in reports.items()}
build=ROOT/'build/bonus989/build-report.json';b=bound(build);sprite=ROOT/'build/bonus985-sprite-helper/build-report.json';bound(sprite);checks['current_binary']=digest(build.parent/'player.exe')==b['binary_sha256']
checks['audio_only_choice_preserves_picture']=all(digest(ROOT/f'build/bonus990-audio/{n}-native/window.png')==digest(ROOT/f'build/bonus990-audio/{n}-md/window.png') for n in range(10,14))
scope='Practical bonus10-13: independent MD Pumbaa, Timon and bug drawings/colors; exact bonus actor ownership; fixed MD background plus matched foreground cells with native geometry/fallbacks and corresponding indexed palette banks; independent Toss134/Hunt281 music. Native intro cards, counters, result cards, effects, catches, rewards, timers and bonus gameplay retained. Actual normal MD10/12/13 backgrounds verified;11 has identical source/initializer/update to12/13. Unknown/flash bodies remain native. Hunt uses original queued MusicOff to avoid native echo music under MD while retaining native pickup effects. Four actual Windows clients inspected; ordinary Hunt catches and current-save continuation checked; all four direct rounds exit. Prior1346 images,924 bounds and1600 palette words preserved. Ending/post-fight presentation and Scar gameplay remain native; no universal MD parity claim.'
paths += [Path(__file__),build,sprite,ROOT/'scripts/Setup.ps1']
for name,key in [('Bug Toss','bug-toss-md'),('Bug Hunt 1','bug-hunt-1-md'),('Bug Hunt 2','bug-hunt-2-md'),('Bug Hunt 3','bug-hunt-3-md')]:paths += [ROOT/f'Play {name} MD.cmd',ROOT/f'profiles/{key}.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope=scope,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
