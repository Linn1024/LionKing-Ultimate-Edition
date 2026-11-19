"""Focused fresh all-MD death audio and an ordinary held opening-skull encounter."""
import csv,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard601-native-music/report.json';r=bound(reference);build=ROOT/'build/graveyard659/build-report.json';bound(build);out=ROOT/'build/graveyard660-skull-audio';out.mkdir();commands={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name in ('death','skull'):
    folder=out/name;folder.mkdir();cmd=r['commands']['seed'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,value in (('--frames','2600' if name=='death' else '2350'),('--hash-at','2600' if name=='death' else '2350'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard619-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_bytes((ROOT/'profiles/graveyard-md.ini').read_bytes())
    if name=='skull':
        i=cmd.index('--practice-level');del cmd[i:i+2];tape=folder/'stand.polled.tape';tape.write_bytes(bytes((0,1))*33+bytes(2000));cmd+=['--load',str(reference.parent/'entry.state'),'--input-polled',str(tape)]
    cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','30']
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_GRAVEYARD_ACTOR_TRACE=str(folder/'actors.csv'),TLK_SPRITE_REPORT=str(folder/'sprites.json')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;print(name,json.loads((folder/'scene.json').read_text())['latched_gameplay'],flush=True)
stems=list(csv.DictReader((out/'death/stems.csv').open()));old=list(csv.DictReader((ROOT/'build/graveyard656-review/audio/stems.csv').open()));checks=dict(old_native_bus_during_md_death=any(int(x['native_peak'])>500 for x in old if 2200<int(x['frame'])<2400),native_bus_removed_during_md_death=all(int(x['native_peak'])==0 for x in stems if 2200<int(x['frame'])<2400),md_death_remains_audible=any(int(x['md_peak'])>1000 for x in stems if 2200<int(x['frame'])<2400))
paths=[Path(__file__),reference,build,ROOT/'build/graveyard656-review/audio/command.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
