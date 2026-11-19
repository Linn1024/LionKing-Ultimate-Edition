"""Resume a real active roar pulse while the porcupine attack is committed."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    out=ROOT/'build/pride-porcupine-roar-saves';out.mkdir();base=ROOT/'build/pride-porcupine38'
    seed=base/'roar-pulse';warm=base/'roar-warm';reports=[seed/'report.json',warm/'report.json']
    for path in reports:bound(path)
    data=(seed/'saved.state').read_bytes();target=re.search(r'wram_sha256=([0-9a-f]{64})',(seed/'run.log').read_text())[1]
    matches=[];at=data.find(bytes.fromhex('5c8cc500f401a303'))
    while at>=0:
        start=at-0xb717
        if start>=0 and hashlib.sha256(data[start:start+0x20000]).hexdigest()==target:matches.append(start)
        at=data.find(bytes.fromhex('5c8cc500f401a303'),at+1)
    assert len(matches)==1
    ram=data[matches[0]:matches[0]+0x20000];(out/'active-pulse-wram.bin').write_bytes(ram)
    word=lambda at:int.from_bytes(ram[at:at+2],'little')
    pointer=lambda at:int.from_bytes(ram[at:at+3],'little')
    row=json.loads((seed/'tree.jsonl').read_text().splitlines()[-1]);assert row['field']==1473
    checks=dict(saved_active_roar=word(0xa698)==16,saved_player_roar=pointer(0xb243)==0xc3589c,
                saved_committed_attack=pointer(0xb743)==0xc15b87 and word(0xb73f)==25,
                saved_health4=word(0x2004)==4)
    commands={}
    for lle in (False,True):
        label='roar-cold'+('-lle' if lle else '')
        cmd=['python',str(ROOT/'tools/capture_pride_porcupine2.py'),'--player',base.relative_to(ROOT).as_posix(),
            '--output',label,'--frames','1600','--tape','build/pride-porcupine-roar-qualification3/late-opposite.polled.tape',
            '--profile','build/pride-porcupine-roar-qualification/resources.ini','--load',(seed/'saved.state').relative_to(ROOT).as_posix(),
            '--poll-offset',str(row['poll_index'])]
        if lle:cmd.append('--lle')
        commands[label]=cmd;subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
        p=base/label/'report.json';reports.append(p);r=bound(p);checks[label+'_capture']=r['result']=='PASS'
        folder=base/label;checks[label+'_warm_guest']=hashes(folder/'run.log')==hashes(warm/'run.log')
        for name in ('window.png','scene.json'):checks[label+'_warm_'+name]=digest(folder/name)==digest(warm/name)
        checks[label+'_remaining_pcm']=pcm(folder/'audio.wav')==pcm(warm/'audio.wav')[len(pcm(seed/'audio.wav')):]
    a=base/'roar-cold';b=base/'roar-cold-lle'
    for name in ('attack.csv','audio.wav','events.csv'):checks['cold_modes_'+name]=digest(a/name)==digest(b/name)
    observer=ROOT/'build/pride-porcupine-roar-observer/roar-late-opposite-aot'
    checks['observer_warm_guest_neutral']=hashes(observer/'run.log')==hashes(warm/'run.log')
    for name in ('window.png','scene.json','audio.wav','events.csv'):checks['observer_warm_'+name]=digest(observer/name)==digest(warm/name)
    paths=[Path(__file__),*reports,observer/'report.json',base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        actual_saved_wram_offset=matches[0],poll_offset=row['poll_index'],ordinary_inputs_only=True,
        guest_rom_or_rng_edits=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
