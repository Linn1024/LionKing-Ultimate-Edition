"""Verify Continue presentation/controls in actual private Windows clients."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-continue-transition-pad-probe';out=base/'capture';out.mkdir()
    build=bound(base/'build-report.json')
    prior=ROOT/'build/pride-continue-bank-ready-probe/capture';reference=bound(prior/'report.json')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};observations={};commands=[]
    cases=[('control',False,124,600,False),('moving124',True,124,460,True),('moving130',True,130,460,True)]
    cases += [(str(age),True,124,age,False) for age in (300,333,350,351,407,408,420,426,432)]
    for name,enabled,confirm,end,moving in cases:
        folder=out/name;folder.mkdir();cmd=reference['commands'][2].copy();cmd[0]=str(base/'player.exe')
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1]=str(folder/filename)
        cmd[cmd.index('--frames')+1]=str(3894+end)
        data=bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
        for age in (124,130):struct.pack_into('<H',data,(3894+age-1)*2,0x8000 if age==confirm else 0)
        if moving:
            for age in range(380,601):struct.pack_into('<H',data,(3894+age-1)*2,0x100)
        tape=folder/'input.tape';tape.write_bytes(data);cmd[cmd.index('--input')+1]=str(tape)
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_CONTINUE_BANK_RECORD=str(prior/'boot/bank.record'),
            TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'),
            TLK_CONTINUE_TRANSITION=str(int(enabled)),TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        rows=list(csv.DictReader((folder/'transition.csv').open()))
        first=next((int(r['field'])-3894 for r in rows if int(r['health'])==4 and int(r['x'])>64),None)
        w,h,rgb=pixels(folder/'window.png')
        observations[name]=dict(first_movement=first,lit=sum(p!=(0,0,0) for p in rgb),
            final=json.loads((folder/'scene.json').read_text())['latched_gameplay'],
            first_level_canvas=next((int(r['field'])-3894 for r in rows if r['level_ready']=='1'),None))
        commands.append(cmd);print(name,observations[name],flush=True)
    checks['disabled_guest_unchanged']=hashes(out/'control/run.log')==hashes(prior/'warm/run.log')
    checks['disabled_window_unchanged']=pixels(out/'control/window.png')==pixels(prior/'warm/window.png')
    checks['first_movement124']=observations['moving124']['first_movement']==433
    checks['first_movement130']=observations['moving130']['first_movement']==439
    checks['black351']=observations['351']['lit']==0
    checks['black407']=observations['407']['lit']==0
    checks['visible408']=observations['408']['lit']>10000
    checks['level_prepared_before_visibility']=observations['408']['first_level_canvas'] is not None and observations['408']['first_level_canvas']<=408
    checks['idle_until432']=observations['432']['final']['player']==[64,1255]
    for name in ('moving124','moving130'):
        g=observations[name]['final'];checks[name+'/health_lives']=g['health']==4 and g['lives']==2 and g['descriptor']==903
    paths=[Path(__file__),base/'build-report.json',prior/'report.json',ROOT/'build/pride-continue-scene-model/report.json']
    report=dict(result='PROTOTYPE_PASS' if all(checks.values()) else 'FAIL',checks=checks,
        observations=observations,commands=commands,public_player_changed=False,
        native_art_and_palette_only=True,independent_audio_and_lifecycle_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
