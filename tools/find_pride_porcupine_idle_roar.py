"""Ordinary late-level roar attempts from a genuine reached/saved checkpoint."""
import csv
import json
import struct
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-idle-roar';out.mkdir()
    base=ROOT/'build/pride-porcupine-roar-observer'
    seed_path=ROOT/'build/pride-porcupine38/idle-roar-seed/report.json';seed=bound(seed_path)
    assert seed['checks']['exit']
    row=json.loads((seed_path.parent/'tree.jsonl').read_text().splitlines()[-1]);assert row['field']==2700
    original=ROOT/'engine/tapes/allbugsF.read.tape';prefix=original.read_bytes()[:row['poll_index']*2]
    profile=ROOT/'build/pride-porcupine-roar-qualification/resources.ini'
    commands={};cases={};reports=[]
    for delay in (16,32,56):
        label=f'idle-roar-{delay}';pads=[0]*delay+[0x80]*20+[0]*(200-delay-20)
        tape=out/(label+'.tail.tape');tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
        full=out/(label+'.poweron.tape');full.write_bytes(prefix+tape.read_bytes())
        cmd=['python',str(ROOT/'tools/capture_pride_porcupine2.py'),'--player',base.relative_to(ROOT).as_posix(),
            '--output',label,'--frames','2900','--tape',tape.relative_to(ROOT).as_posix(),'--profile',profile.relative_to(ROOT).as_posix(),
            '--load',(seed_path.parent/'saved.state').relative_to(ROOT).as_posix()]
        commands[label]=cmd;subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
        p=base/label/'report.json';r=bound(p);reports.append(p)
        rows=list(csv.DictReader((base/label/'attack.csv').open())) if (base/label/'attack.csv').exists() else []
        first_by_actor={}
        for r in rows:
            if r['pc']=='c15c64':first_by_actor.setdefault(r['actor'],r)
        cases[label]=dict(first_attack_by_actor=first_by_actor,events=list(csv.DictReader((base/label/'events.csv').open())),
            full_tape=full.relative_to(ROOT).as_posix())
        print(label,[(a,r['field'],r['timer'],r['player_action']) for a,r in first_by_actor.items()],flush=True)
    paths=[Path(__file__),seed_path,original,profile,base/'build-report.json',*reports]
    report=dict(result='OBSERVED_LATE_ENTRY' if any(r['timer']=='28' for c in cases.values() for r in c['first_attack_by_actor'].values()) else 'NO_LATE_ENTRY_FOUND',
        cases=cases,commands=commands,prefix_poll_index=row['poll_index'],ordinary_controls_only=True,guest_rom_or_rng_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
