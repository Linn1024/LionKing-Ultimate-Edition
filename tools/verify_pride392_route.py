"""Compare one supported MD gameplay route before/after table migration."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/pride392-route';out.mkdir(exist_ok=True)
build=ROOT/'build/pride390/build-report.json';bound(build)
prior=ROOT/'build/pride382/build-report.json';bound(prior)
setup=ROOT/'build/pride391/report.json';assert bound(setup)['result']=='PASS'
reference=ROOT/'build/pride381-route/report.json';ref=bound(reference)
route=ROOT/'build/pride-normal-completion/route.polled.tape';profile=ROOT/'build/pride-launch4/completion2/320/resources.ini'
keys=(('--asset-cache','scene_cache'),('--final-menu-assets','menu_assets'),('--final-native-assets','native_final_assets'),('--title-bank-assets','title_bank_assets'),('--hud-assets','hud_assets'),('--sprite-assets','sprite_assets'),('--caption-assets','caption_assets'),('--checkpoint-assets','checkpoint_assets'),('--revival-assets','revival_assets'),('--native-hud-assets','native_hud_assets'))
commands={};codes={}
for label,data,player in (('before',ROOT/'game-data',prior.parent/'player.exe'),('after',ROOT/'build/pride391/data',build.parent/'player.exe')):
    folder=out/label;folder.mkdir(exist_ok=True);m=json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
    cmd=ref['commands']['after'].copy();cmd[0]=str(player)
    i=cmd.index('--save-at');del cmd[i:i+3]
    cmd[cmd.index('--input-polled')+1]=str(route);cmd[cmd.index('--hash-at')+1]='1800,3852,5000'
    for flag,key in keys:cmd[cmd.index(flag)+1]=str(data/m[key]['file'])
    for flag,key in (('--rom','snes'),('--md-rom','megadrive')):cmd[cmd.index(flag)+1]=str(data/m['roms'][key]['file'])
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    (folder/'resources.ini').write_bytes(profile.read_bytes())
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy';commands[label]=cmd
    with (folder/'run.log').open('wb') as log:codes[label]=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    print(label,codes[label],flush=True)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda label:re.findall(pattern,(out/label/'run.log').read_text())
scene=json.loads((out/'after/scene.json').read_text())
checks=dict(exits=all(c==0 for c in codes.values()),gameplay_samples_preserved=rows('before')==rows('after') and len(rows('after'))==3,picture_preserved=digest(out/'before/window.png')==digest(out/'after/window.png'),audio_preserved=digest(out/'before/audio.wav')==digest(out/'after/audio.wav'),first_level_completed=scene['level']==1,profile_accepted='Profile rejected' not in (out/'after/run.log').read_text())
paths=[Path(__file__),build,prior,setup,reference,route,profile]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,scope='One ordinary authored power-on route with supported MD gameplay/art/audio, including all migrated table consumers, to level1. No loads, practice or guest edits; before/after samples, final client and entire PCM. Existing credited All Bugs-derived input remains ignored.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,scene['level'],flush=True)
