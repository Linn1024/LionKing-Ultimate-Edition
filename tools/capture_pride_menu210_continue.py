"""Fresh ordinary-input native Continue idle/YES/NO clocks on current139."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

template=ROOT/'build/pride-menu198-clocks/report.json'
ref=bound(template)
build=ROOT/'build/pride-menu209-observer/build-report.json'
bound(build)
fixture=ROOT/'build/pride-final-continue-fixture/report.json'
bound(fixture)
original=fixture.parent/'neutral-after-final.tape'
raw=original.read_bytes()
prefix=raw[:3894*2]
out=ROOT/'build/pride-menu210-continue'
out.mkdir()
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
clean['SDL_VIDEODRIVER']='dummy'
commands={};observations={};checks={}
for case in ('idle','yes','no'):
    folder=out/case;folder.mkdir()
    words=list(struct.unpack('<'+'H'*(len(prefix)//2),prefix))+[0]*(6500-len(prefix)//2)
    if case!='idle':words[4500]=0x80
    if case=='no':words[4470:4474]=[0x100]*4
    tape=folder/'ordinary.tape';tape.write_bytes(struct.pack('<'+'H'*len(words),*words))
    profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    cmd=ref['commands']['snes-aot'].copy();cmd[0]=str(build.parent/'player.exe')
    cmd[cmd.index('--input-polled')]='--input'
    for flag,value in (('--input',tape),('--resource-profile',profile),('--config',config),
        ('--frames',6000),('--hash-at',','.join(map(str,range(3500,6001)))),
        ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')):
        cmd[cmd.index(flag)+1]=str(value)
    env=dict(clean,TLK_MENU197=str(folder/'menu.csv'),TLK_MENU_CURSOR208=str(folder/'cursor.csv'))
    with (folder/'run.log').open('wb') as f:
        rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    commands[case]=cmd;checks[case+'_exit']=rc==0
    assert rc==0,(case,rc)
    rows=list(csv.DictReader((folder/'menu.csv').open()))
    cursors=list(csv.DictReader((folder/'cursor.csv').open()))
    assert all(None not in r for r in cursors)
    kinds=set(r['kind'] for r in rows)-{'frame'}
    frames=[r for r in rows if r['kind']=='frame']
    first={k:next(r for r in rows if r['kind']==k) for k in kinds}
    observations[case]=dict(first_callbacks=first,callback_counts={k:sum(r['kind']==k for r in rows) for k in kinds},
        cursor_events=[r for r in cursors if r['kind'] in ('ContinueTransitionConfirm','ContinueTitleExit')],
        changes=[r for i,r in enumerate(frames) if not i or any(r[k]!=frames[i-1][k] for k in ('scene','health','spares','credits','brightness'))])
    checks[case+'_ordinary_credit_bearing_fatal']=('FinalSceneBegin' in first and int(first['FinalSceneBegin']['credits'])>0)
    print(case,'first',{k:(v['field'],v['credits']) for k,v in first.items()},flush=True)
    (out/'partial.json').write_text(json.dumps(observations,indent=2)+'\n')
paths=[Path(__file__),template,build,fixture,original]
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if all(checks.values()) else 'INCOMPLETE_ROUTE',
    checks=checks,commands=commands,observations=observations,
    scope='Fresh native ordinary Normal route followed by neutral/YES/NO controller schedules. '
          'Read-only observed clocks/cursor; no state/credit/health edits. Production neutrality separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('CAPTURED' if all(checks.values()) else 'INCOMPLETE_ROUTE',checks,flush=True)
