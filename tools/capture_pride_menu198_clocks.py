"""Fresh ordinary native/MD final-timeline menu observations on current139."""
import csv
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm

observer = ROOT/'build/pride-menu197-observer'
bp = observer/'build-report.json'
bound(bp)
base = ROOT/'build/pride-hyena-entrance139'
public_report = base/'build-report.json'
bound(public_report)
template = ROOT/'build/pride-porcupine186-polled/report.json'
reference = bound(template)
route_report = ROOT/'build/pride-final-arena-route2/report.json'
bound(route_report)
tape = route_report.parent/'ordinary.polled.tape'
out = ROOT/'build/pride-menu198-clocks'
out.mkdir()
checks = {}
commands = {}
observations = {}
clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
clean['SDL_VIDEODRIVER'] = 'dummy'
for source in ('snes','md'):
    folder = out/source
    folder.mkdir()
    profile = folder/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\n'
                       'gameplay.levels.pride_lands.final_life = '+source+'\n')
    cfg = folder/'host.ini'
    cfg.write_text('opengl = 0\nscale = 2\n')
    for mode in ('observer','aot','lle'):
        run = folder/mode
        run.mkdir()
        cmd = reference['commands']['hard'].copy()
        cmd[0] = str((observer if mode=='observer' else base)/'player.exe')
        i = cmd.index('--load');del cmd[i:i+2]
        for flag, value in (
                ('--config',cfg),('--resource-profile',profile),('--input-polled',tape),
                ('--frames',6500),('--hash-at',','.join(map(str,range(4000,6501)))),
                ('--dump-window',run/'window.png'),('--dump-scene',run/'scene.json'),
                ('--wav',run/'audio.wav')):
            cmd[cmd.index(flag)+1] = str(value)
        if mode=='lle':cmd.append('--lle')
        env = dict(clean)
        if mode=='observer':env['TLK_MENU197']=str(run/'menu.csv')
        with (run/'run.log').open('wb') as f:
            rc = subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,
                                timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        commands[source+'-'+mode] = cmd
        checks[source+'-'+mode+'_exit'] = rc==0
        print(source,mode,'exit',rc,flush=True)
        assert rc==0
        if mode=='observer':
            rows = list(csv.DictReader((run/'menu.csv').open()))
            special = [r for r in rows if r['kind']!='frame']
            frames = [r for r in rows if r['kind']=='frame']
            entries = [r for r in frames if int(r['scene'])==0xc0057b]
            changes = [r for i,r in enumerate(frames) if not i or any(r[k]!=frames[i-1][k] for k in ('scene','health','spares','credits','brightness'))]
            observations[source] = dict(callback_counts={k:sum(r['kind']==k for r in special) for k in set(r['kind'] for r in special)},
                first_callbacks={k:next(r for r in special if r['kind']==k) for k in set(r['kind'] for r in special)},
                menu_first=entries[0] if entries else None,menu_last=entries[-1] if entries else None,changes=changes)
            print(source,'menu',entries[0]['field'] if entries else None,'callbacks',observations[source]['callback_counts'],flush=True)
        else:
            import re
            observed = folder/'observer'
            pattern = r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
            actual = re.findall(pattern,(run/'run.log').read_text())
            expected = re.findall(pattern,(observed/'run.log').read_text())
            checks[source+'-'+mode+'_all2501_guest_samples_exact'] = actual==expected and len(actual)==2501
            checks[source+'-'+mode+'_whole_pcm_exact'] = pcm(run/'audio.wav')==pcm(observed/'audio.wav')
            checks[source+'-'+mode+'_client_exact'] = digest(run/'window.png')==digest(observed/'window.png')
            checks[source+'-'+mode+'_scene_exact'] = (run/'scene.json').read_bytes()==(observed/'scene.json').read_bytes()
    (out/'partial.json').write_text(json.dumps(observations,indent=2)+'\n')
paths = [Path(__file__),bp,public_report,template,route_report,tape]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',
    checks=checks,commands=commands,observations=observations,
    scope='Fresh ordinary Hard arena route to native and selected MD final menus. '
          'Read-only callback/brightness/owner observations with production AOT/LLE neutrality; '
          'no independently selectable artwork implemented by this capture.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
