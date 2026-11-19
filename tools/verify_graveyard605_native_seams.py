"""Short native controls at moving-bone completion and pillar impact; no route replay."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard592-native-owners/report.json';r=bound(reference);build=ROOT/'build/graveyard599/build-report.json';bound(build)
out=ROOT/'build/graveyard605-native-seams';out.mkdir(exist_ok=True);commands={};checks={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for start,end in ((14248,14300),(16410,16760)):
    for name,exe in [('old',ROOT/'build/cant-wait579/player.exe'),('current',build.parent/'player.exe')]:
        folder=out/f'{start}-{name}';folder.mkdir(exist_ok=True);cmd=r['cases'][0]['command'].copy();cmd[0]=str(exe);i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in (('--frames',str(end)),('--hash-at',str(end)),('--load',str(reference.parent/str(start)/'entry.state')),('--input-polled',str(reference.parent/str(start)/'remaining.polled.tape')),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav')),('--wav-seconds','8')):cmd[cmd.index(flag)+1]=value
        (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n')
        with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[f'{start}-{name}']=cmd
    a=out/f'{start}-old';b=out/f'{start}-current';pattern=r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+'
    checks[f'{start}_native_guest']=re.findall(pattern,(a/'run.log').read_text())==re.findall(pattern,(b/'run.log').read_text());checks[f'{start}_native_pcm']=digest(a/'audio.wav')==digest(b/'audio.wav');checks[f'{start}_actual_window']=ImageChops.difference(Image.open(a/'window.png'),Image.open(b/'window.png')).getbbox() is None
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
