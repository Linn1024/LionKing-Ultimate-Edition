"""Compare ordinary committed-attack roar protocols with the original MD phases."""
import argparse
import csv
import json
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--probe',action='store_true');args=ap.parse_args()
    suffix='probe' if args.probe else 'qualification';out=ROOT/('build/pride-porcupine-roar-'+suffix);out.mkdir()
    base=ROOT/'build/pride-porcupine-roar-observer'
    original=ROOT/'build/md-porcupine-roar3/report.json';reference=bound(original)
    seed_source=ROOT/'build/pride-porcupine-contact-search/report.json';seed=bound(seed_source)
    original_tape=ROOT/'engine/tapes/allbugsF.read.tape';prefix=original_tape.read_bytes()[:seed['anchor_poll_offset']*2]
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.simba.roar = md\n')
    checks={};commands={};reports={};observations={}
    cases=[('early',32,8,True,'roar32'),('late',48,8,True,'roar48'),('held-turn',32,0,True,None),('control',32,8,False,'turn-control')]
    if args.probe:cases=cases[:1]
    for label,delay,gap,roar,original_case in cases:
        pads=[0]*delay+[0x200]+[0]*gap+([0x80] if roar else [0])*20+[0]*(200-delay-gap-21)
        tape=out/(label+'.polled.tape');tape.write_bytes(prefix+struct.pack('<'+'H'*len(pads),*pads))
        pair=[]
        for lle in (False,True):
            run_label='roar-'+suffix+'-'+label+('-lle' if lle else '-aot');pair.append(base/run_label)
            cmd=['python',str(ROOT/'tools/capture_pride_porcupine2.py'),'--player',base.relative_to(ROOT).as_posix(),
                 '--output',run_label,'--frames','1600','--tape',tape.relative_to(ROOT).as_posix(),'--profile',profile.relative_to(ROOT).as_posix()]
            if lle:cmd.append('--lle')
            commands[run_label]=list(map(str,cmd));subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
            path=base/run_label/'report.json';reports[path]=bound(path);checks[run_label+'_capture']=reports[path]['result']=='PASS'
        a,b=pair;checks[label+'_mode_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        for name in ('window.png','scene.json','audio.wav','attack.csv','events.csv'):checks[label+'_mode_'+name]=digest(a/name)==digest(b/name)
        rows=list(csv.DictReader((a/'attack.csv').open()))
        phases=[r for r in rows if r['pc']=='c15c64']
        active=[r for r in phases if int(r['roar_active'])]
        transitions=[]
        for row in active:
            after=[r for r in phases if r['actor']==row['actor'] and int(r['field'])==int(row['field'])+1]
            if after:transitions.append(dict(before=row,after=after[0],countdown_continues=int(after[0]['timer'])==int(row['timer'])-1))
        observations[label]=dict(active=active,transitions=transitions,original_case=original_case)
        if label in ('early','late'):
            expected=reference['cases'][original_case]['active_attack_observations']
            checks[label+'_actual_roar_pulse']=bool(active) and all(r['player_action']=='c3589c' for r in active)
            checks[label+'_same_original_timer_phase']=[r['timer'] for r in active]==[r['timer'] for r in expected]
            checks[label+'_attack_continues']=len(transitions)==len(active) and all(r['countdown_continues'] for r in transitions)
        else:checks[label+'_no_pulse']=not active
        print(label,'active',[(r['field'],r['timer'],r['roar_active']) for r in active],flush=True)
    paths=[Path(__file__),original,seed_source,original_tape,base/'build-report.json',*reports]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',probe_only=args.probe,checks=checks,
                commands=commands,observations=observations,ordinary_controls_only=True,guest_rom_or_rng_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
