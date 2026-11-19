"""Observe old/new bone emission boundaries in private clones; do not publish these trace builds."""
import collections,csv,json,os,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard597-opening/report.json';r=bound(reference);fixture=ROOT/'build/graveyard592-native-owners/report.json';bound(fixture)
out=ROOT/'build/graveyard610-sound-seams';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44';commands={};records={};pictures={};values={};builds=[]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,base in [('old',ROOT/'build/graveyard599'),('current',ROOT/'build/graveyard609')]:
    bp=base/'build-report.json';b=bound(bp);builds.append(bp);folder=out/name;folder.mkdir(exist_ok=True);source=folder/'audio.c';s=(base/'game/tlk_audio.c').read_text()
    if name=='old':
        s=s.replace('static int music_active','static unsigned gy_trace_pre;\nstatic int music_active',1)
        s=s.replace('graveyard_opcode(cpu,pc-2);','gy_trace_pre=1;graveyard_opcode(cpu,pc-2);gy_trace_pre=0;')
    phase='gy_trace_pre' if name=='old' else 'before'
    anchor='TlkMdSoundCommand(2,value);effect_tail();';assert s.count(anchor)==1
    s=s.replace(anchor,anchor+'\n        static FILE *cue_trace;if(!cue_trace){cue_trace=fopen("'+(folder/'cues.csv').as_posix()+'","w");fputs("frame,actor,pc,value,before,counter\\n",cue_trace);}\n        fprintf(cue_trace,"%u,%04x,%06x,%u,%u,%u\\n",frame,actor,pc,value,'+phase+',word(actor+0x2c));fflush(cue_trace);')
    source.write_text(s);compile=b['compiles']['audio'].copy();old=(cwd/compile[compile.index('-o')+1]).resolve();obj=folder/'audio.obj'
    for flag,value in (('-c',source),('-o',obj),('-MF',folder/'audio.d'),('-MT',obj)):compile[compile.index(flag)+1]=str(value)
    with (folder/'compile.log').open('wb') as log:subprocess.run(compile,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1;inputs[indices[0]]=obj.as_posix();rsp=folder/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (folder/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(folder/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    shutil.copy2(base/'genesis_plus_gx_libretro.dll',folder/'genesis_plus_gx_libretro.dll')
    cmd=r['commands']['all'].copy();cmd[0]=str(folder/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,value in (('--frames','14960'),('--hash-at','14960'),('--load',str(fixture.parent/'14248/entry.state')),('--input-polled',str(fixture.parent/'14248/remaining.polled.tape')),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):
        if flag in ('--config','--resource-profile'):Path(value).write_bytes(Path(r['commands']['all'][r['commands']['all'].index(flag)+1]).read_bytes())
        cmd[cmd.index(flag)+1]=value
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    records[name]=list(csv.DictReader((folder/'cues.csv').open()));commands[name]=cmd;pictures[name]=Image.open(folder/'window.png');values[name]=json.loads((folder/'scene.json').read_text())['latched_gameplay']
    print(name,records[name],flush=True)
def repeats(rows):
    return [(a,b) for i,a in enumerate(rows) for b in rows[i+1:] if a['actor']==b['actor'] and a['pc']==b['pc'] and a['value']==b['value'] and abs(int(a['frame'])-int(b['frame']))<=1]
checks=dict(old_duplicate_proven=bool(repeats(records['old'])),corrected_one_per_event=not repeats(records['current']),fewer_duplicate_cues=len(records['current'])<len(records['old']),gameplay_preserved=values['current']==values['old'],actual_picture_preserved=ImageChops.difference(pictures['current'],pictures['old']).getbbox() is None,audio_changes=digest(out/'current/audio.wav')!=digest(out/'old/audio.wav'))
paths=[Path(__file__),reference,fixture,*builds]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,records=records,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
