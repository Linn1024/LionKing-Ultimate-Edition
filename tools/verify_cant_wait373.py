"""Exercise prepared second-level foreground, source choices and moving gameplay."""
import json,os,re,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/cant-wait372/build-report.json';bound(build)
helper=ROOT/'build/cant-wait371-cmake/build-report.json';h=bound(helper)
data=ROOT/'build/cant-wait371-setup';m=json.loads((data/'install.json').read_text());assert m['scene_cache']['sha256']==h['cache_sha256']
out=ROOT/'build/cant-wait373';out.mkdir(exist_ok=True);commands={}
reference=ROOT/'build/cant-wait363/report.json';ref=bound(reference)
keys=(('--asset-cache','scene_cache'),('--final-menu-assets','menu_assets'),('--final-native-assets','native_final_assets'),('--title-bank-assets','title_bank_assets'),('--hud-assets','hud_assets'),('--sprite-assets','sprite_assets'),('--caption-assets','caption_assets'),('--checkpoint-assets','checkpoint_assets'),('--revival-assets','revival_assets'),('--native-hud-assets','native_hud_assets'))
def run(label):
    folder=out/label;folder.mkdir(exist_ok=True);cmd=ref['commands']['moving-new' if label=='moving' else 'initial-md'].copy();cmd[0]=str(build.parent/'player.exe')
    if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,key in keys:cmd[cmd.index(flag)+1]=str(data/m[key]['file'])
    for flag,key in (('--rom','snes'),('--md-rom','megadrive')):cmd[cmd.index(flag)+1]=str(data/m['roms'][key]['file'])
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    profile='schema = 1\ngame = snes\ndisplay.viewport = md\n'
    if label!='native':profile+='graphics.scenery = md\n'
    if label=='native-foreground':profile+='graphics.scenery.foreground = snes\n'
    (folder/'resources.ini').write_text(profile)
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    if label=='moving':cmd+=['--save-at','1610',str(out/'moving.state')]
    commands[label]=cmd
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    print(label,rc,flush=True);return label,rc
with ThreadPoolExecutor(max_workers=2) as pool:exits=dict(pool.map(run,('native','md','native-foreground','moving')))
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text())
checks=dict(exits=all(v==0 for v in exits.values()),actual_setup_used=m['scene_cache']['cant_wait_foreground']=={'matched':12391,'total':12400},native_picture_preserved=digest(out/'native/window.png')==digest(reference.parent/'native/window.png'),guest_preserved=rows(out/'md/run.log')==rows(out/'native/run.log')==rows(out/'native-foreground/run.log'),artwork_source_independent=digest(out/'md/window.png')!=digest(out/'native-foreground/window.png'),moving_guest_preserved=rows(out/'moving/run.log')==rows(reference.parent/'moving-new/run.log'),moving_audio_preserved=digest(out/'moving/audio.wav')==digest(reference.parent/'moving-new/audio.wav'),moving_foreground_visible=digest(out/'moving/window.png')!=digest(reference.parent/'moving-new/window.png'))
paths=[Path(__file__),build,helper,reference,data/'install.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,scope='Actual native Setup output; native control, independent foreground art, selected moving/jumping/roaring scene, unchanged guest/audio. Geometry safety from installer per-cell shape/height mapping; nine unmatched cells remain native.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
