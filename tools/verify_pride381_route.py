"""One ordinary first-level route before/after install-time contact preparation."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/pride381-route';out.mkdir(exist_ok=True)
build=ROOT/'build/pride379/build-report.json';bound(build)
prior=ROOT/'build/cant-wait372/build-report.json';bound(prior)
setup=ROOT/'build/pride380/report.json';assert bound(setup)['result']=='PASS'
reference=ROOT/'build/cant-wait365-ride/report.json';ref=bound(reference)
keys=(('--asset-cache','scene_cache'),('--final-menu-assets','menu_assets'),('--final-native-assets','native_final_assets'),('--title-bank-assets','title_bank_assets'),('--hud-assets','hud_assets'),('--sprite-assets','sprite_assets'),('--caption-assets','caption_assets'),('--checkpoint-assets','checkpoint_assets'),('--revival-assets','revival_assets'),('--native-hud-assets','native_hud_assets'))
commands={};codes={}
for label,data,player in (('before',ROOT/'game-data',prior.parent/'player.exe'),('after',ROOT/'build/pride380/data',build.parent/'player.exe')):
    folder=out/label;folder.mkdir(exist_ok=True);m=json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
    cmd=ref['command'].copy();cmd[0]=str(player)
    if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
    cmd[cmd.index('--frames')+1]='5000';cmd[cmd.index('--hash-at')+1]='1800,3852,5000'
    for flag,key in keys:cmd[cmd.index(flag)+1]=str(data/m[key]['file'])
    for flag,key in (('--rom','snes'),('--md-rom','megadrive')):cmd[cmd.index(flag)+1]=str(data/m['roms'][key]['file'])
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    (folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud = md\ngameplay.levels.pride_lands.contacts = md\n')
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/name)
    cmd+=['--wav',str(folder/'audio.wav'),'--save-at','3750',str(folder/'fight.state')]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
    commands[label]=cmd
    with (folder/'run.log').open('wb') as log:codes[label]=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    print(label,codes[label],flush=True)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda label:re.findall(pattern,(out/label/'run.log').read_text())
scene=json.loads((out/'after/scene.json').read_text())
checks=dict(exits=all(c==0 for c in codes.values()),all_guest_samples_preserved=rows('before')==rows('after') and len(rows('after'))==3,picture_preserved=digest(out/'before/window.png')==digest(out/'after/window.png'),audio_preserved=digest(out/'before/audio.wav')==digest(out/'after/audio.wav'),first_level_completed=scene['level']==1,installed_data_loaded='resource_cache=loaded' in (out/'after/run.log').read_text(),profile_accepted='Profile rejected' not in (out/'after/run.log').read_text())
# An explicitly supplied obsolete cache must stop before play, with a useful error.
reject=commands['after'].copy();reject[reject.index('--asset-cache')+1]=str(ROOT/'game-data/scenes-v1.cache');reject[reject.index('--frames')+1]='1'
with (out/'rejected.log').open('wb') as log:rc=subprocess.run(reject,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW).returncode
checks['outdated_data_requests_setup']=rc==8 and 'Run Setup.cmd again' in (out/'rejected.log').read_text()
paths=[Path(__file__),build,prior,setup,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,reject_command=reject,scope='One ordinary All Bugs controller prefix through first-level victory and bonus to level1, MD terrain tags and selected artwork; before/after gameplay, picture and PCM. One outdated-cache rejection. No full-game/source/save matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,scene['level'],flush=True)
