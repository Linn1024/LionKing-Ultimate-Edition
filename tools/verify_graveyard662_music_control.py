"""Preserve native music/FX and confirm native FX survive selected MD music ownership."""
import csv,json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard660-skull-audio/report.json';r=bound(reference);out=ROOT/'build/graveyard662-music-control';out.mkdir();commands={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label in ('old-native','native','native-fx'):
    folder=out/label;folder.mkdir();cmd=r['commands']['death'].copy();cmd[0]=str(ROOT/('build/graveyard652/player.exe' if label=='old-native' else 'build/graveyard659/player.exe'))
    for flag,value in (('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+('audio.music.elephant_graveyard = md\n' if label=='native-fx' else ''))
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_AUDIO_STEMS=str(folder/'stems.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[label]=cmd;print(label,flush=True)
a=out/'old-native';b=out/'native';pattern=r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+';stems=list(csv.DictReader((out/'native-fx/stems.csv').open()))
checks=dict(native_pcm=digest(a/'audio.wav')==digest(b/'audio.wav'),native_guest=re.findall(pattern,(a/'run.log').read_text())==re.findall(pattern,(b/'run.log').read_text()),native_window=ImageChops.difference(Image.open(a/'window.png'),Image.open(b/'window.png')).getbbox() is None,native_hurt_fx_retained=any(int(x['native_peak'])>500 and int(x['md_peak'])>500 for x in stems if 1712<int(x['frame'])<1740))
paths=[Path(__file__),reference,ROOT/'build/graveyard659/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
