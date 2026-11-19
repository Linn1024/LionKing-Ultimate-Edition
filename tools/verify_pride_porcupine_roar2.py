"""Separate a real damage-canceled roar from an unobstructed late roar pulse."""
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
    out=ROOT/'build/pride-porcupine-roar-qualification2';out.mkdir()
    base=ROOT/'build/pride-porcupine-roar-observer';production=ROOT/'build/pride-porcupine38'
    old_path=ROOT/'build/pride-porcupine-roar-qualification/report.json';old=bound(old_path)
    md_path=ROOT/'build/md-porcupine-roar3/report.json';md=bound(md_path)
    assert old['result']=='FAIL' and sum(old['checks'].values())==38 and len(old['checks'])==40
    checks={key:value for key,value in old['checks'].items() if not key.startswith('late_')};commands={};reports={}
    profile=old_path.parent/'resources.ini'
    prefix=(ROOT/'engine/tapes/allbugsF.read.tape').read_bytes()[:1096*2]
    pads=[0x100]*4+[0]*44+[0x200]+[0]*8+[0x80]*20+[0]*123
    assert len(pads)==200
    tape=out/'late-spaced.polled.tape';tape.write_bytes(prefix+struct.pack('<'+'H'*len(pads),*pads))
    def capture(player,label,recording,lle=False):
        cmd=['python',str(ROOT/'tools/capture_pride_porcupine2.py'),'--player',player.relative_to(ROOT).as_posix(),
             '--output',label,'--frames','1600','--tape',recording.relative_to(ROOT).as_posix(),'--profile',profile.relative_to(ROOT).as_posix()]
        if lle:cmd.append('--lle')
        commands[label]=cmd;subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
        p=player/label/'report.json';reports[p]=bound(p);checks[label+'_capture']=reports[p]['result']=='PASS'
    capture(base,'roar-late-spaced-aot',tape)
    capture(base,'roar-late-spaced-lle',tape,True)
    capture(production,'roar-control',old_path.parent/'control.polled.tape')
    def equal(label,a,b,names):
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        for name in names:checks[label+'_'+name]=digest(a/name)==digest(b/name)
    equal('late_spaced_modes',base/'roar-late-spaced-aot',base/'roar-late-spaced-lle',('window.png','scene.json','audio.wav','attack.csv','events.csv'))
    equal('observer_control_neutral',base/'roar-qualification-control-aot',production/'roar-control',('window.png','scene.json','audio.wav','events.csv'))
    rows=list(csv.DictReader((base/'roar-late-spaced-aot/attack.csv').open()))
    phases=[r for r in rows if r['pc']=='c15c64'];active=[r for r in phases if int(r['roar_active'])]
    original=md['cases']['roar48']['active_attack_observations']
    checks['late_spaced_actual_pulse']=bool(active) and all(r['player_action']=='c3589c' and r['health']=='4' for r in active)
    checks['late_spaced_same_original_phase']=[r['timer'] for r in active]==[r['timer'] for r in original]
    follows=[]
    for r in active:
        following=[x for x in phases if x['actor']==r['actor'] and int(x['field'])==int(r['field'])+1]
        follows.append(bool(following) and int(following[0]['timer'])==int(r['timer'])-1)
    checks['late_spaced_attack_continues']=bool(follows) and all(follows)
    canceled=list(csv.DictReader((base/'roar-qualification-late-aot/attack.csv').open()))
    hits=[r for r in canceled if r['pc']=='c15c8f' and r['contact_result']=='ffff' and r['player_action']=='c3589c']
    after=[r for r in canceled if hits and r['pc']=='c15c64' and int(r['field'])==int(hits[0]['field'])+1]
    checks['cancel_real_hit_during_roar']=bool(hits) and hits[0]['player_flags']=='04' and hits[0]['attacker']=='7eb713'
    checks['cancel_roar_to_hurt']=bool(after) and after[0]['player_action']=='c35d6c' and after[0]['health']=='3'
    checks['cancel_no_activation']=not any(int(r['roar_active']) for r in canceled)
    original_cancel_path=md_path.parent/'roar64/calls.csv'
    original_cancel=list(csv.DictReader(original_cancel_path.open()))
    original_hits=[r for r in original_cancel if r['pc']=='19a81c' and r['player_action']=='1966c6']
    original_after=[r for r in original_cancel if original_hits and r['pc']=='19a446' and int(r['field'])==int(original_hits[0]['field'])+1]
    checks['original_cancel_hit_during_roar']=bool(original_hits) and original_hits[0]['player_flags']=='04' and original_hits[0]['attacker']=='ff98ce'
    checks['original_cancel_roar_to_hurt']=bool(original_after) and original_after[0]['player_action']=='196b4c' and original_after[0]['health']=='3'
    checks['original_cancel_no_activation']=not md['cases']['roar64']['active_attack_observations']
    checks['original_successful_pulses_continue']=all(md['cases'][name]['transitions'] and all(x['countdown_continues'] for x in md['cases'][name]['transitions']) for name in ('roar32','roar48'))
    checks['retained_failed_equal_input_expectation']=old['result']=='FAIL'
    for p in old['source_sha256']:
        if p.endswith('/report.json') or p.endswith('/build-report.json'):bound(ROOT/p)
    paths=[Path(__file__),old_path,md_path,original_cancel_path,base/'build-report.json',production/'build-report.json',*reports]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        late_active=active,canceled_first_contact=hits[:1],original_canceled_first_contact=original_hits[:1],
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
