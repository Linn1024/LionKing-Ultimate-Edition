"""Focused native control, independent bone choices and first actual Graveyard encounters."""
import collections,csv,gzip,json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
reference=ROOT/'build/graveyard588-audio/report.json';r=bound(reference);build=ROOT/'build/graveyard596/build-report.json';bound(build)
out=ROOT/'build/graveyard597-opening';out.mkdir(exist_ok=True);commands={};sounds={};logs={};scenes={};images={}
shared=['audio.effects.simba.'+x for x in ('roar','hurt','bounce','roll','ledge_grab')]+['audio.effects.world.'+x for x in ('hyena_hurt','hyena_pant','hyena_jump','hyena_taunt','health_bug','full_health_bug','life_bug','roar_bug','harmful_bug','bonus_bug','checkpoint','continue_token','pickup_arrival')]
specific=['audio.effects.world.graveyard.'+x for x in ('vulture','bone_shake','bone_platform','bone_break','pillar')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,exe,selected in [('old',ROOT/'build/cant-wait579/player.exe',()),('native',build.parent/'player.exe',()),('all',build.parent/'player.exe',shared+specific),('bones',build.parent/'player.exe',specific[1:4])]:
    folder=out/name;folder.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(exe)
    for flag,value in (('--frames','13820'),('--hash-at','13500,13633,13820'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav')),('--wav-seconds','12')):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\naudio.music.elephant_graveyard = md\n'+''.join(x+' = md\n' for x in selected))
    pipe=None;runenv=dict(env,TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_HYENA_VOICE_TRACE=str(folder/'hyena.csv'))
    if name=='all':
        cmd+=['--save-at','13640',str(folder/'pending.state')];pipe=JsonPipe(folder/'tree.jsonl.gz');runenv['TLK_SOFT_TREE_LOG']=pipe.name
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=runenv,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    if pipe:
        pipe.finish();rows=[json.loads(x) for x in gzip.open(folder/'tree.jsonl.gz','rt')];saved=next(x for x in rows if x['field']==13640);tape=Path(cmd[cmd.index('--input-polled')+1]);(folder/'pending.polled.tape').write_bytes(tape.read_bytes()[saved['poll_index']*2:])
    commands[name]=cmd;sounds[name]=collections.Counter((x['selector'],x['value']) for x in csv.DictReader((folder/'commands.csv').open()));logs[name]=(folder/'run.log').read_text();scenes[name]=json.loads((folder/'scene.json').read_text());images[name]=Image.open(folder/'window.png')
pattern=r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+'
checks=dict(profiles_loaded=all('Saved resource profile loaded' in log for log in logs.values()),native_guest_preserved=re.findall(pattern,logs['old'])==re.findall(pattern,logs['native']),native_pcm_preserved=digest(out/'old/audio.wav')==digest(out/'native/audio.wav'),native_window_preserved=ImageChops.difference(images['old'],images['native']).getbbox() is None,actual_graveyard=all(x['level']==2 and x['latched_gameplay']['descriptor']==0x3eb for x in scenes.values()),hyena_entry_pcm4=sounds['all'][('19','4')]>0,hyena_pant_pcm7=sounds['all'][('19','7')]>0,simba_hurt_pcm1=sounds['all'][('19','1')]>0,simba_bounce_fm123=sounds['all'][('2','123')]>0,bone_break_and_release=sounds['all'][('2','105')]==2,health_fm98=sounds['all'][('2','98')]>0,bones_independent=sounds['bones'][('2','105')]==2 and not any(sounds['bones'][k] for k in [('19','4'),('19','7'),('19','1'),('2','123'),('2','98')]),visible_play_preserved=all(ImageChops.difference(images['native'],im).getbbox() is None for im in images.values()),gameplay_values_preserved=all(x['latched_gameplay']==scenes['native']['latched_gameplay'] for x in scenes.values()),md_audio_changes=digest(out/'all/audio.wav')!=digest(out/'native/audio.wav'))
paths=[Path(__file__),reference,build,ROOT/'build/graveyard594-cues/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,shared_leaves=shared,specific_leaves=specific,sounds={k:[dict(selector=a[0],value=a[1],count=n) for a,n in v.items()] for k,v in sounds.items()},scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,{k:dict(v) for k,v in sounds.items()},flush=True)
