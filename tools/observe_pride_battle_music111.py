"""Explicit read-only audio-call and host-frame observers on current103 inputs."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

base=ROOT/'build/pride-hyena-probe103';bp=base/'build-report.json';b=bound(bp)
reference=base/'fights104/report.json';ref=bound(reference);assert ref['result']=='PASS'
out=ROOT/'build/pride-battle-music111';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['host'].copy();cmd[cmd.index('-c')]='-E'
for flag,value in [('-o',out/'host-original.i'),('-MT',out/'host.obj'),('-MF',out/'host.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'preprocess.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
text=(out/'host-original.i').read_text();anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {';assert text.count(anchor)==1
text=text.replace(anchor,'static _Bool BattlePreviousFrame(uint32 inputs) {')
text+='''
_Bool __wrap_RtlRunFrame(uint32 inputs) {
    _Bool result=BattlePreviousFrame(inputs);
    const char *path=getenv("TLK_BATTLE_FRAME_OBSERVER");static FILE *f;
    if(path && snes_frame_counter>=3700 && snes_frame_counter<=3950) {
        if(!f){f=fopen(path,"w");if(f)fputs("field,scene,action,timer,audio_wait,x,y,player_x,player_y\\n",f);}
        #define BW(at) (g_ram[(at)]|((unsigned)g_ram[(at)+1]<<8))
        #define BP(at) (BW(at)|((unsigned)g_ram[(at)+2]<<16))
        if(f){fprintf(f,"%u,%06x,%06x,%u,%u,%u,%u,%u,%u\\n",(unsigned)snes_frame_counter,BP(0xdf),BP(0xba43),BW(0xba3f),BW(0xabf),BW(0xba1b),BW(0xba1d),BW(0xb21b),BW(0xb21d));fflush(f);}
        #undef BW
        #undef BP
    }
    return result;
}
'''
(out/'host.i').write_text(text)
observer=ROOT/'tools/pride_battle_music_observer110.c';s=observer.read_text().replace('void __real_TlkMdSoundCommand(unsigned,unsigned);','').replace('__wrap_TlkMdSoundCommand','BattleObservedSoundCommand').replace('__real_TlkMdSoundCommand(selector,value)','TlkMdSoundCommand(selector,value)')
(out/'command-observer.c').write_text(s)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles={}
for label,source in [('host',out/'host.i'),('audio',Path(b['compiles']['audio'][b['compiles']['audio'].index('-c')+1])),('observer',out/'command-observer.c')]:
    cmd=b['compiles']['probe' if label=='observer' else label].copy();old=Path(cmd[cmd.index('-o')+1])
    for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
    if label=='audio':cmd+=['-DTlkMdSoundCommand=BattleObservedSoundCommand']
    with (out/(label+'-compile.log')).open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
    if label=='observer':inputs.insert(0,(out/'observer.obj').as_posix())
    else:
        matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(matches)==1
        inputs[matches[0]]=(out/(label+'.obj')).as_posix()
    compiles[label]=cmd
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
cmd=ref['commands']['native'].copy();cmd[0]=str(out/'player.exe')
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
with (out/'resources.ini').open('a') as f:f.write('\naudio.music.pride_lands = md\n')
for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
env.update(SDL_VIDEODRIVER='dummy',TLK_BATTLE_MUSIC_OBSERVER=str(out/'commands.csv'),TLK_BATTLE_FRAME_OBSERVER=str(out/'frames.csv'))
with (out/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
rows=list(csv.DictReader((out/'frames.csv').open()));calls=list(csv.DictReader((out/'commands.csv').open()))
battle=[r for r in calls if r['selector']=='1' and r['value']=='134'];jumps=[r for r in rows if r['action']=='c148b6']
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda p:re.findall(pattern,p.read_text())
checks=dict(exit=rc==0,all4320_guest_fields_preserved=hashes(out/'run.log')==hashes(reference.parent/'native/run.log'),
    battle_and_jump_observed=bool(battle) and bool(jumps),all251_frame_observations=len(rows)==251)
paths=[Path(__file__),bp,reference,observer,rsp,out/'host.i',out/'host-original.i',out/'command-observer.c']
(out/'report.json').write_text(json.dumps(dict(result='BATTLE_MUSIC_TIMELINE_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,battle_music_calls=battle,first_native_weak_jump=jumps[0] if jumps else None,
    command=cmd,compiles=compiles,scope='Current103 ordinary Normal fight with only Pride music MD; original game input objects retained, explicit read-only host/audio observers. Original MD counterpart separately captured109.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Timeline',checks,'battle',battle,'first jump',jumps[:1],flush=True)
