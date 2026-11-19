"""Retain close-range cancellation and add the unobstructed opposite-side pulse."""
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
    out=ROOT/'build/pride-porcupine-roar-qualification3';out.mkdir()
    base=ROOT/'build/pride-porcupine-roar-observer'
    previous_path=ROOT/'build/pride-porcupine-roar-qualification2/report.json';previous=bound(previous_path)
    assert previous['result']=='FAIL' and sum(previous['checks'].values())==53 and len(previous['checks'])==56
    checks={k:v for k,v in previous['checks'].items() if not k.startswith('late_spaced_')}
    profile=ROOT/'build/pride-porcupine-roar-qualification/resources.ini'
    source_tape=ROOT/'engine/tapes/allbugsF.read.tape'
    pads=[0x200]*24+[0]*24+[0x100]+[0]*8+[0x80]*20+[0]*123
    assert len(pads)==200
    tape=out/'late-opposite.polled.tape';tape.write_bytes(source_tape.read_bytes()[:1096*2]+struct.pack('<'+'H'*len(pads),*pads))
    reports={};commands={}
    for lle in (False,True):
        label='roar-late-opposite'+('-lle' if lle else '-aot')
        cmd=['python',str(ROOT/'tools/capture_pride_porcupine2.py'),'--player',base.relative_to(ROOT).as_posix(),
            '--output',label,'--frames','1600','--tape',tape.relative_to(ROOT).as_posix(),'--profile',profile.relative_to(ROOT).as_posix()]
        if lle:cmd.append('--lle')
        commands[label]=cmd;subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
        p=base/label/'report.json';reports[p]=bound(p);checks[label+'_capture']=reports[p]['result']=='PASS'
    a=base/'roar-late-opposite-aot';b=base/'roar-late-opposite-lle'
    checks['opposite_modes_guest']=hashes(a/'run.log')==hashes(b/'run.log')
    for name in ('window.png','scene.json','audio.wav','attack.csv','events.csv'):checks['opposite_modes_'+name]=digest(a/name)==digest(b/name)
    phases=[r for r in csv.DictReader((a/'attack.csv').open()) if r['pc']=='c15c64']
    active=[r for r in phases if int(r['roar_active'])]
    checks['opposite_actual_late_pulse']=bool(active) and all(r['player_action']=='c3589c' and r['health']=='4' and 0<int(r['timer'])<=28 for r in active)
    checks['opposite_pulse_original_timer26']=[r['timer'] for r in active]==['26']
    following=[]
    for r in active:
        after=[x for x in phases if x['actor']==r['actor'] and int(x['field'])==int(r['field'])+1]
        following.append(bool(after) and int(after[0]['timer'])==int(r['timer'])-1)
    checks['opposite_attack_continues']=bool(following) and all(following)
    checks['opposite_player_is_left_of_enemy']=bool(active) and all(int(r['player_x'])<int(r['actor_x']) for r in active)
    checks['previous_spaced_cancellation_retained']=previous['result']=='FAIL'
    for p in previous['source_sha256']:
        if p.endswith('/report.json') or p.endswith('/build-report.json'):bound(ROOT/p)
    paths=[Path(__file__),previous_path,profile,source_tape,base/'build-report.json',*reports]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,late_active=active,
        ordinary_controls_only=True,guest_rom_or_rng_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[(r['field'],r['timer'],r['roar_active']) for r in active],[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
