"""Check actual Game Over exit clients against ordinary original MD pictures."""
import array
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-game-over13';build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-final-arena-fixture/report.json';fixture=bound(source);fatal=fixture['fatal_field']
    refs=[ROOT/'build/pride-game-over-exits-original/report.json',ROOT/'build/pride-game-over-held-original/report.json']
    cases={}
    for ref in refs:
        for key,row in bound(ref)['cases'].items():cases[key]=(ref,row)
    prepared=ROOT/'build/pride-final-native-installed/actual install';manifest=prepared/'install.json';info=json.loads(manifest.read_text())
    out=base/'verification2';out.mkdir();checks={};commands={};timings={};frames={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    def run(width,case,age,label=None,load=None,save=False,lle=False,enabled=True):
        name=f'{width}-{case}-{label or age}';folder=out/name;folder.mkdir();tape=out/f'{case}.tape'
        if not tape.exists():
            row=cases[case][1];raw=bytearray(6500*2);struct.pack_into('<H',raw,(fatal-1)*2,0x200)
            pressed=row['pressed_age'];end=row.get('held_through',pressed)
            if pressed is not None:
                for at in range(pressed,end+1):struct.pack_into('<H',raw,(fatal+at-1)*2,0x1000 if row['button']==8 else 0x8000)
            tape.write_bytes(raw)
        cmd=fixture['commands']['control0'].copy();cmd[0]=str(base/'player.exe');at=cmd.index('--input-polled');del cmd[at:at+2]
        cmd+=['--input',str(tape),'--final-menu-assets',str(prepared/info['menu_assets']['file']),
            '--final-native-assets',str(prepared/info['native_final_assets']['file']),'--wav',str(folder/'audio.wav'),'--wav-seconds','120']
        for flag,value in [('--resource-profile',out/f'{width}.ini'),('--config',out/'host.ini'),('--frames',fatal+age),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load/'saved.state')
        if save:cmd+=['--save-at',str(fatal+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        actual=dict(env,TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        if not enabled:actual.pop('TLK_FINAL_MD_ART')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[name]=cmd;checks[name+'_exit']=r.returncode==0
        print(name,'exit',r.returncode,flush=True);return folder
    r5=[0,4,8,12,17,21,25,29];g6=[0,8,17,25,34,42,51,59]
    expand=lambda v:v<<3|v>>2
    rgb={r<<11|g<<5|b:(expand(r),expand(r5[g6.index(g)]),expand(b)) for r in r5 for g in g6 for b in r5}
    def compare(folder,width,case,age):
        ref,row=cases[case];frame=next(r for r in row['frames'] if r['age']==age)
        raw=zlib.decompress((ref.parent/'frames'/(frame['frame_sha256']+'.rgb565.z')).read_bytes())
        assert hashlib.sha256(raw).hexdigest()==frame['frame_sha256']
        original=[rgb[v] for v in array.array('H',raw)];expected=[];start=(320-width)//2
        for y in range(224):
            line=[c for x in range(start,start+width) for c in (original[y*320+x],)*2];expected.extend(line);expected.extend(line)
        return pixels(folder/'window.png')==(width*2,448,expected)
    selected={
        'a124':(124,125,130,140,142,143), 'a140':(140,141,150,158,159),
        'none':(323,324,325,330,342,343), 'start140':(140,141,159),
        'a100':(180,), 'a121':(180,), 'a122':(180,), 'a123':(180,),
        'held100':(180,), 'held123':(180,), 'held124':(125,143)}
    for width in (256,320):
        (out/f'{width}.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\ngameplay.levels.pride_lands.final_life = md\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
        for case,ages in selected.items():
            for age in ages:
                folder=run(width,case,age,save=(case,age) in [('a124',130),('a140',150),('none',330)])
                frames[width,case,age]=folder;checks[f'{width}-{case}-{age}_whole_original_picture']=compare(folder,width,case,age)
        for case,saved,target in [('a124',130,142),('a140',150,158),('none',330,342)]:
            cold=run(width,case,target,label=f'cold{target}',load=frames[width,case,saved])
            target_folder=frames[width,case,target]
            checks[f'{width}-{case}_cold_client']=pixels(cold/'window.png')==pixels(target_folder/'window.png')
            checks[f'{width}-{case}_cold_guest']=hashes(cold/'run.log')==hashes(target_folder/'run.log')
            checks[f'{width}-{case}_cold_pcm']=pcm(cold/'audio.wav')==pcm(target_folder/'audio.wav')[len(pcm(frames[width,case,saved]/'audio.wav')):]
        lle=run(width,'none',342,label='lle342',lle=True)
        checks[f'{width}_lle_client']=pixels(lle/'window.png')==pixels(frames[width,'none',342]/'window.png')
        checks[f'{width}_lle_guest']=hashes(lle/'run.log')==hashes(frames[width,'none',342]/'run.log')
        checks[f'{width}_lle_pcm']=pcm(lle/'audio.wav')==pcm(frames[width,'none',342]/'audio.wav')
        native=run(width,'a140',150,label='native150',enabled=False)
        checks[f'{width}_art_independent_guest']=hashes(native/'run.log')==hashes(frames[width,'a140',150]/'run.log')
        checks[f'{width}_art_independent_pcm']=pcm(native/'audio.wav')==pcm(frames[width,'a140',150]/'audio.wav')
        # Observe the remaining title delay, without presenting it as a match.
        title=run(width,'none',700,label='title700')
        rows=list(csv.reader((title/'exit.csv').open()));first=next((int(r[1]) for r in rows if r[0]=='frame' and r[2]=='c005ab' and int(r[5])>0),None)
        timings[str(width)]=dict(original_first_picture=cases['none'][1]['next_picture'],native_first_picture=first,
            remaining_fields=first-cases['none'][1]['next_picture'] if first else None)
        cold=run(width,'none',700,label='cold-title700',load=frames[width,'none',330])
        checks[f'{width}_cold_title_client']=pixels(cold/'window.png')==pixels(title/'window.png')
        checks[f'{width}_cold_title_guest']=hashes(cold/'run.log')==hashes(title/'run.log')
        checks[f'{width}_cold_title_pcm']=pcm(cold/'audio.wav')==pcm(title/'audio.wav')[len(pcm(frames[width,'none',330]/'audio.wav')):]
    paths=[Path(__file__),build,source,*refs,manifest,ROOT/'engine/runner/tlk_continue_menu.h',ROOT/'engine/runner/pride/final/pride_final_runtime.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,title_timing_observed_not_matched=timings,
        scope='Whole Game Over menu/fade/black pictures, input edges, selected-art independence and cold title handoff; title delay remains open',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],timings,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
