"""Independent gameplay choices from the pillar checkpoint; retain a current mixed-play save."""
import gzip,hashlib,json,os,re,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/graveyard592-native-owners/report.json';r=bound(reference);build=ROOT/'build/graveyard621/build-report.json';bound(build)
out=ROOT/'build/graveyard626-choices';out.mkdir(exist_ok=True);commands={};results={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,leaves in [('native',()),('health',('vulture_health',)),('bounds',('vulture_bounds',)),('both',('vulture_health','vulture_bounds'))]:
    folder=out/name;folder.mkdir(exist_ok=True);cmd=r['cases'][-1]['command'].copy();cmd[0]=str(build.parent/'player.exe')
    for flag,value in (('--load',str(reference.parent/'16410/entry.state')),('--input-polled',str(reference.parent/'16410/remaining.polled.tape')),('--frames','17700'),('--hash-at','17700'),('--sprite-assets',str(ROOT/'build/graveyard619-helper/sprites.assets')),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):cmd[cmd.index(flag)+1]=value
    i=cmd.index('--save-at');cmd[i+1:i+3]=['17700',str(folder/'entry.state')]
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+''.join('gameplay.levels.elephant_graveyard.'+x+' = md\n' for x in leaves))
    trace=JsonPipe(folder/'tree.jsonl.gz')
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_GRAVEYARD_GAMEPLAY_TRACE=str(folder/'gameplay.csv'),TLK_HITBOX_TRACE=str(folder/'hitboxes.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
    metadata=trace.finish();last=trace.latest();source=Path(cmd[cmd.index('--input-polled')+1]);(folder/'remaining.polled.tape').write_bytes(source.read_bytes()[last['poll_index']*2:])
    scene=json.loads((folder/'scene.json').read_text());raw=(folder/'entry.state').read_bytes();needle=struct.pack('<HH',*scene['latched_gameplay']['player']);expected=re.findall(r'wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text())[-1];found=[];at=0
    while (at:=raw.find(needle,at))>=0:
        offset=at-0xb21b;at+=1
        if offset>=0 and hashlib.sha256(raw[offset:offset+0x20000]).hexdigest()==expected:found.append(offset)
    assert len(found)==1;ram=raw[found[0]:found[0]+0x20000];(folder/'wram.bin').write_bytes(ram)
    actors=[]
    for actor in range(0xb293,0xc213,128):
        descriptor=int.from_bytes(ram[actor+4:actor+7],'little')
        if descriptor in (0xc58cca,0xc58cd8,0xc58ce6,0xc58c74):actors.append(dict(actor=hex(actor),descriptor=hex(descriptor),hp=struct.unpack_from('<H',ram,actor+0x2a)[0],position=struct.unpack_from('<HH',ram,actor+8)))
    results[name]=dict(scene=scene['latched_gameplay'],actors=actors,poll_index=last['poll_index'],health_applied=(folder/'gameplay.csv').exists(),bounds_applied=(folder/'hitboxes.csv').exists());commands[name]=cmd;print(name,results[name],flush=True)
checks=dict(independent_health=results['health']['health_applied'] and not results['health']['bounds_applied'],independent_bounds=results['bounds']['bounds_applied'] and not results['bounds']['health_applied'],both_applied=results['both']['health_applied'] and results['both']['bounds_applied'],native_retained=not results['native']['health_applied'] and not results['native']['bounds_applied'],all_alive=all(x['scene']['health']>0 for x in results.values()))
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,cases=results,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
