"""Play through Continue and further deaths to verify a fresh final-life episode."""
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
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-final-scene-lifecycle-probe';out=base/'second-episode';out.mkdir()
    build=bound(base/'build-report.json')
    reference=ROOT/'build/pride-final-scene-save-probe/capture/report.json';report=bound(reference)
    original=ROOT/'build/pride-final-continue-fixture/neutral-after-final.tape'
    tape=out/'two-episodes.tape';tape.write_bytes(original.read_bytes()[:3894*2]+
        struct.pack('<5000H',*[0x8000 if n==124 else (0x100 if n>=433 else 0) for n in range(1,5001)]))
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[]
    def run(name,end,save=False,load=None):
        folder=out/name;folder.mkdir();cmd=report['commands'][0].copy();cmd[0]=str(base/'player.exe')
        # Source command writes a save; every run gets its own reviewed destination.
        i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        cmd[cmd.index('--frames')+1]=str(end);cmd[cmd.index('--input')+1]=str(tape)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(end),str(folder/'saved.state')]
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        if not load:env['TLK_CONTINUE_BANK_RECORD']=str(ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record')
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd);return folder
    route=run('route',3894+5000)
    events=list(csv.DictReader((route/'points.csv').open()))
    finals=[r for r in events if r['pc']=='c089b9' and r['spares']=='0' and r['descriptor']=='c00387']
    assert len(finals)>=2,finals
    second=int(finals[1]['field']);print('second final-life entry',second,flush=True)
    direct=run('direct',second+144);saved=run('save100',second+100,True)
    resumed=run('resume144',second+144,load=saved/'saved.state')
    raw=(saved/'saved.state').read_bytes();native_size=struct.unpack_from('<I',raw,20)[0];metadata=96+native_size+96
    field,entry,age,flags=struct.unpack_from('<4I',raw,metadata)
    confirmed=struct.unpack_from('<Q',raw,metadata+52)[0]
    checks=dict(second_fatal_starts_fresh=finals[1]['redirected']=='0',
        second_epoch_saved=entry==second and age==100 and field==second+100,
        previous_continue_clock_cleared=confirmed==0,
        new_origin_and_target=bool(flags&4) and bool(flags&8),
        second_scene_cold_window=pixels(resumed/'window.png')==pixels(direct/'window.png'))
    source=[Path(__file__),base/'build-report.json',reference,original]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,second_fatal_field=second,
        final_entries=finals,commands=commands,public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in source},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
