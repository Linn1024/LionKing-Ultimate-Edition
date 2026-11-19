"""Exercise Continue's bank cache, cold fallback, PCM and actual controls."""
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
    base=ROOT/'build/pride-continue-bank-probe2';out=base/'capture';out.mkdir()
    build=bound(base/'build-report.json');prior=ROOT/'build/pride-continue-fast-reload-probe/capture'
    reference=bound(prior/'report.json')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    observations={};commands=[];checks={}
    for name in ('boot','cold','warm','moving'):
        folder=out/name;folder.mkdir();cmd=reference['commands'][1].copy()
        cmd[0]=str(base/'player.exe')
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json')]:
            cmd[cmd.index(flag)+1]=str(folder/filename)
        if name=='boot':
            i=cmd.index('--load');del cmd[i:i+2];cmd[cmd.index('--frames')+1]='1200'
        if name=='moving':
            tape=folder/'moving.tape';data=bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
            for age in range(550,601):struct.pack_into('<H',data,(3894+age-1)*2,0x100)
            tape.write_bytes(data);cmd[cmd.index('--input')+1]=str(tape)
        cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','120']
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        if name in ('warm','moving'):env['TLK_CONTINUE_BANK_RECORD']=str(out/'boot/bank.record')
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
        bank=list(csv.DictReader((folder/'bank.csv').open()))
        frames=[r for r in csv.DictReader((folder/'exit.csv').open()) if r['kind']=='frame' and int(r['age'])>124]
        observations[name]=dict(bank_events=bank,gameplay=json.loads((folder/'scene.json').read_text())['latched_gameplay'],
            first_healthy=next((int(r['age']) for r in frames if 0<int(r['health'])<10),None),
            black_intervals=[(int(r['age']),r['a_or_lit']=='0') for n,r in enumerate(frames) if n and
                (r['a_or_lit']=='0')!=(frames[n-1]['a_or_lit']=='0')])
        commands.append(cmd);print(name,observations[name],flush=True)
    checks['boot_cache_ready']=(out/'boot/bank.record').is_file()
    checks['cold_falls_back']=any(r['event']=='apply' and r['ok']=='0' for r in observations['cold']['bank_events'])
    checks['cold_guest_unchanged']=hashes(out/'cold/run.log')==hashes(prior/'fast/run.log')
    checks['cold_window_unchanged']=pixels(out/'cold/window.png')==pixels(prior/'fast/window.png')
    for name in ('warm','moving'):
        checks[name+'/applied']=any(r['event']=='apply' and r['ok']=='1' for r in observations[name]['bank_events'])
        g=observations[name]['gameplay']
        checks[name+'/main_health_lives']=g['descriptor']==903 and g['health']==4 and g['lives']==2
    checks['warm_spawn']=observations['warm']['gameplay']['player']==[64,1255]
    checks['movement']=observations['moving']['gameplay']['player'][0]>100
    paths=[Path(__file__),base/'build-report.json',prior/'report.json']
    report=dict(result='PROTOTYPE_PASS' if all(checks.values()) else 'FAIL',checks=checks,
        observations=observations,commands=commands,public_player_changed=False,
        audio_fidelity_and_lifecycle_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
