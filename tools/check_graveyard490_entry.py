"""Current-build direct third-level entry: bounded native/MD scenery views and saves."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait462-rhino/report.json';r=bound(reference)
build=ROOT/'build/cant-wait482/build-report.json';bound(build)
out=ROOT/'build/graveyard490-entry';out.mkdir(exist_ok=True);commands={};scenes={};checks={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label,extra in (('native',''),('md','graphics.scenery = md\ngraphics.sprites.simba.cub = md\naudio.music.elephant_graveyard = md\n')):
    folder=out/label;folder.mkdir(exist_ok=True);cmd=r['commands']['native'].copy();cmd[0]=str(build.parent/'player.exe')
    i=cmd.index('--input');del cmd[i:i+2]
    for flag,value in (('--practice-level','2'),('--frames','1800'),('--hash-at','1800'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
    cmd+=['--save-at','1800',str(folder/'entry.state')]
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n')
    (folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+extra)
    run_env=dict(env,TLK_WRAM_DUMP='1800',TLK_WRAM_DIR=str(folder))
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=run_env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    scene=json.loads((folder/'scene.json').read_text());scenes[label]=scene
    checks[label+'_owned_entry']=scene['level']==2 and scene['latched_gameplay']['descriptor']==0x3eb and scene['latched_gameplay']['health']>0
    checks[label+'_save_created']=(folder/'entry.state').stat().st_size>1000
    commands[label]=cmd
checks['presentation_choices_visible']=digest(out/'native/window.png')!=digest(out/'md/window.png')
paths=[Path(__file__),reference,build,ROOT/'docs/graveyard-goal.md']
inventory={label:sorted({(p.get('actor_descriptor',0),p.get('pose',0),p.get('palette',0)) for p in scene['pieces']}) for label,scene in scenes.items()}
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,piece_inventory=inventory,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,inventory,flush=True)
