"""Aggregate original gate evidence and bound the sampled native boss probe domain."""
import collections
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-enemy-gates96';out.mkdir();paths=[Path(__file__)]
    proofs={}
    for name in ['pride-hyena-pounce-gate93','pride-hyena-walk-gate94','pride-hyena-walk-coordinates95','pride-hyena-motion87']:
        p=ROOT/'build'/name/'report.json';proofs[name]=bound(p);paths.append(p)
    raw=proofs['pride-hyena-walk-gate94'];aligned=proofs['pride-hyena-walk-coordinates95']
    behavior=[r for r in raw['failures'] if r['snes'][:5]+r['snes'][6:]!=r['md'][:5]+r['md'][6:]]
    groups=collections.Counter(r['terrain'] for r in behavior)
    samples=[];tags=collections.Counter();actions=collections.Counter()
    for difficulty in ('normal','hard'):
        reference=ROOT/f'build/pride-hyena-recovery/snes/{difficulty}/frames.json'
        expected=json.loads(reference.read_text());paths.append(reference)
        for row in expected:
            p=reference.parent/f'hl_wram_{row["field"]}.bin';ram=p.read_bytes();paths.append(p)
            word=lambda at:struct.unpack_from('<H',ram,at)[0]
            ptr=lambda at:int.from_bytes(ram[at:at+3],'little')
            actor=0xba13;x,y=word(actor+8),word(actor+10)
            assert (x,y)==(row['x'],row['y']) and ptr(actor+4)==0xc58c68
            assert len(ram)==0x20000 and (word(0xd0),word(0xd4))==(200,80)
            assert ptr(actor+0x30)==row['action']
            map_at=ptr(0xe9)-0x7e0000;attrs=ptr(0xf2)-0x7e0000;points=[]
            for offset in (-32,32):
                for subtract in (8,16):
                    cell=max(0,y-subtract)//16*200+(x+offset)//16*2
                    assert 0<=cell<16000
                    tag=ram[attrs+(word(map_at+cell)&0xfff8)//2]
                    points.append(dict(offset_x=offset,subtract_y=subtract,cell=cell,tag=tag));tags[tag]+=1
            actions[row['action']]+=1
            samples.append(dict(difficulty=difficulty,field=row['field'],x=x,y=y,action=row['action'],points=points))
    (out/'native-snapshot-probe-domain.json').write_text(json.dumps(samples,indent=2)+'\n')
    public=ROOT/'build/pride-menu-enable86/bindings/report.json';release=bound(public);paths.append(public)
    checks=dict(pounce_originals_agree=proofs['pride-hyena-pounce-gate93']['result']=='POUNCE_GATES_VERIFIED',
                raw_walk_difference_retained=raw['result']=='FAIL' and len(raw['failures'])==13032,
                wrong_expected_count_identified=raw['fixtures']==67328 and not raw['checks']['all_cases_executed'],
                behavior_differences_only_two_slope_tags=groups=={0x4e:780,0x4f:504},
                aligned_original_walk_decisions_agree=aligned['result']=='WALK_COORDINATE_CAUSE_VERIFIED' and all(aligned['checks'].values()) and aligned['fixtures']==67328,
                all_prior_native_boss_snapshots_checked=len(samples)==1022,
                sampled_native_boss_map_probes_avoid_both_slopes=not(tags[0x4e] or tags[0x4f]) and sum(tags.values())==4088,
                qualified_public86_still_bound=release['result']=='PASS' and all(release['checks'].values()))
    report=dict(result='ENEMY_GATES_AND_PROBE_DIFFERENCE_QUALIFIED' if all(checks.values()) else 'FAIL',checks=checks,
                raw_walk_fixtures=raw['fixtures'],raw_walk_exact_record_differences=len(raw['failures']),behavior_differences=len(behavior),
                behavior_differences_by_tag=dict(groups),native_snapshot_fields=len(samples),native_snapshot_probe_tags=dict(tags),native_snapshot_actions=dict(actions),
                coordinate_difference='SNES C0C801/C0C82B pass actorY; MD0023F4/00242E pass actorY-8. Their common lookup then subtracts8 on both platforms.',
                raw_wall_tags_are_platform_specific=True,corrected_grid_count=67328,
                scope='Original full walking selection on synthetic uniform maps; research alignment explains behavioral difference. Snapshot inventory is native boss map data sampled at both probe heights, not a replay of MD fights or proof that slope interactions are unreachable. Earlier action precedence and final movement remain separate.',
                next_step='Capture original wall-wrapper inputs/outputs during ordinary hyena roaming and turns. Verify native C0C5FE/C0C6E3 adapter seams and caller/descriptor guards before implementing an independent hyena turn-probe-height source.',
                runtime_or_capabilities_changed=False,full_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
