"""Check all-MD direct Graveyard startup and a native control after the title-input guard fix."""
import gzip,json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/graveyard601-native-music/report.json';r=bound(reference);build=ROOT/'build/graveyard652/build-report.json';bound(build);out=ROOT/'build/graveyard653-md-launcher';out.mkdir();commands={};rows={};scenes={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label in ('md','native','old-native'):
    folder=out/label;folder.mkdir();cmd=r['commands']['seed'].copy();cmd[0]=str(ROOT/('build/graveyard644/player.exe' if label=='old-native' else 'build/graveyard652/player.exe'));i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,value in (('--frames','1800'),('--hash-at','1800'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard619-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text() if label=='md' else 'schema = 1\ngame = snes\n')
    trace=JsonPipe(folder/'tree.jsonl.gz')
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    trace.finish();rows[label]=trace.latest();scenes[label]=json.loads((folder/'scene.json').read_text());commands[label]=cmd;print(label,scenes[label]['latched_gameplay'],flush=True)
c={x[0]:x for x in rows['md']['choices']};needed=('display.viewport','graphics.scenery.foreground','graphics.scenery.background','graphics.sprites.enemies.vultures.frames','graphics.sprites.enemies.hyenas.frames','graphics.sprites.bones.palette','graphics.hud.frames','audio.music.elephant_graveyard.track','audio.music.elephant_graveyard.death','audio.effects.world.graveyard.vulture','audio.effects.world.graveyard.pillar','gameplay.levels.elephant_graveyard.vulture_health','gameplay.levels.elephant_graveyard.vulture_bounds');pattern=r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+'
checks=dict(all_md_selected=all(c[n][4]==2 for n in needed),unsupported_explicit_native=all(c[n][4]==1 for n in ('gameplay.simba.movement','gameplay.simba.combat','gameplay.levels.other','audio.voices')),playable_graveyard=scenes['md']['level']==2 and scenes['md']['latched_gameplay']['descriptor']==0x3eb and scenes['md']['latched_gameplay']['health']>0 and rows['md']['macro_index']==rows['md']['macro_length'],native_guest_preserved=re.findall(pattern,(out/'native/run.log').read_text())==re.findall(pattern,(out/'old-native/run.log').read_text()),native_window_preserved=ImageChops.difference(Image.open(out/'native/window.png'),Image.open(out/'old-native/window.png')).getbbox() is None)
paths=[Path(__file__),reference,build,ROOT/'profiles/graveyard-md.ini',ROOT/'Play Elephant Graveyard MD.cmd']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
