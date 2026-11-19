"""Bind the observed NPC branch to its original instructions and return state."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player/bounce-npc-audit4'
    rp=base/'report.json';report=bound(rp)
    assert report['result']=='OBSERVED' and all(report['checks'].values())
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    # Original LDA $0ABF; BNE $44E8, then the jump constructor on fallthrough.
    assert rom[0x144bd:0x144c2]==bytes.fromhex('adbf0ad026')
    assert rom[0x144d8:0x144dc]==bytes.fromhex('22b648c1')
    runs={}
    for name in ('native','bounce'):
        with (base/name/'npc.csv').open() as stream:runs[name]=list(csv.DictReader(stream))
    gates={n:[r for r in rows if r['phase']=='gate'] for n,rows in runs.items()}
    transitions=[]
    for index,(a,b) in enumerate(zip(gates['native'],gates['bounce'])):
        assert a['npc_bytes']==b['npc_bytes'] and a['player_bytes']==b['player_bytes']
        assert a['input']==b['input'] and a['rng']==b['rng']
        assert a['raw_abf']==a['acc'] and b['raw_abf']==b['acc']
        if bool(int(a['acc'],16))==bool(int(b['acc'],16)):continue
        returns={}
        for name,row in (('native',a),('bounce',b)):
            assert int.from_bytes(bytes.fromhex(row['npc_bytes'])[0x2c:0x2e],'little')==0
            assert row['action']=='c143ae' and int(row['player_x'])<0x5d0
            returned=next(r for r in runs[name] if r['phase']=='return' and r['field']==row['field'])
            predicted='c143ae' if int(row['acc'],16) else 'c148b6'
            assert returned['action']==predicted
            returns[name]=dict(field=int(row['field']),gate_value=row['acc'],returned_action=returned['action'])
        transitions.append(dict(gate_index=index+1,states_identical_before_branch=True,returns=returns))
    assert len(transitions)==1
    destination=ROOT/'build/pride-lizard-launch-work/bounce-gate-report.json';assert not destination.exists()
    paths=[Path(__file__),rp,ROOT/'docs/pride-lands-reference.md']
    result=dict(result='OBSERVED_ORIGINAL_NPC_GATE_TRANSITION_EXPLAINED',transitions=transitions,
        original_branch='C144C0 BNE C144E8',fallthrough_constructor='C144D8 JSL C148B6',
        sample_scope='Matched recorded gates on this ordinary Pride route only',
        underlying_audio_scheduling_cause_proven=False,production_changed=False,
        full_gameplay_equivalence_proven=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination.write_text(json.dumps(result,indent=2)+'\n');print(result['result'],transitions,flush=True)


if __name__=='__main__':main()
