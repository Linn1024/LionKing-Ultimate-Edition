"""Check live second-level scenery and unchanged playable guest behavior."""
import json,os,re,struct,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/cant-wait362/build-report.json';bound(build)
out=ROOT/'build/cant-wait363';out.mkdir(exist_ok=True)
ref=json.loads((ROOT/'build/level-caption340/report.json').read_text());commands={}
tape=out/'move.tape';pads=[0]*2400
for i in range(1530,1670):pads[i]=0x100 | (0x8000 if i%40<12 else 0) | (0x4000 if i%97<3 else 0)
tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
def run(label):
    folder=out/label;folder.mkdir(exist_ok=True);cmd=ref['commands']['1'].copy()
    cmd[0]=str(ROOT/('build/hyena-hud356/player.exe' if label=='moving-old' else 'build/cant-wait362/player.exe'))
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    profile='schema = 1\ngame = snes\ndisplay.viewport = md\n'
    if label!='native':profile+='graphics.scenery.background = md\ngraphics.scenery.palettes = md\n'
    (folder/'resources.ini').write_text(profile)
    field=2200 if label.startswith('moving') else 1800
    cmd[cmd.index('--frames')+1]=str(field);cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1500,field+1,10)))
    if label.startswith('moving'):cmd+=['--input',str(tape)]
    if label=='moving-new':cmd+=['--save-at','1610',str(out/'moving.state')]
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    commands[label]=cmd
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    print(label,rc,flush=True);return label,rc
with ThreadPoolExecutor(max_workers=2) as pool:exits=dict(pool.map(run,('native','initial-md','moving-old','moving-new')))
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda name:re.findall(pattern,(out/name/'run.log').read_text())
native_reference=ROOT/'build/level-caption340/1'
checks=dict(exits=all(v==0 for v in exits.values()),native_picture_unchanged=digest(out/'native/window.png')==digest(native_reference/'window.png'),initial_md_visible=digest(out/'native/window.png')!=digest(out/'initial-md/window.png'),initial_guest_unchanged=rows('native')==rows('initial-md'),moving_guest_unchanged=rows('moving-old')==rows('moving-new'),moving_audio_unchanged=digest(out/'moving-old/audio.wav')==digest(out/'moving-new/audio.wav'),moving_md_visible=digest(out/'moving-old/window.png')!=digest(out/'moving-new/window.png'),current_moving_save_written=(out/'moving.state').exists())
paths=[Path(__file__),build,ROOT/'build/level-caption340/report.json',tape]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,scope='Ordinary level-select controller macro followed by neutral or right/jump/roar inputs. Live MD background versus native; unchanged guest/audio. Foreground, monkey/cub controls remain native.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
