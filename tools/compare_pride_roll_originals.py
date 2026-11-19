"""Compare original rolling protocols and retain all contact/position divergences.

Shared uninterrupted roll samples do not prove the full environmental/damage
path. Initial spawn offsets must not be mistaken for a different roll speed.
"""
import hashlib
import argparse
import json
from collections import Counter
from audit_scenes import ROOT
from compare_pride_movement import value

STATES={0xc32b24:0x193a1c,0xc31ac3:0x1929be,0xc33226:0x194070,
        0xc31e57:0x192d32,0xc336b1:0x19450c,0xc32389:0x19327c,
        0xc3554c:0x196406,0xc356f3:0x196566,0xc311e1:0x19214c,0xc302ef:0x191278}
ROLL={0xc3554c:0x196406,0xc356f3:0x196566}
HURT={0xc35d6c:0x196b4c,0xc35f3c:0x196d04}
STATES.update(HURT)  # Original constants/live entries audited by pride_hurt_pair_audit.py.


def state(row,source):
    return (row['words'][24]|row['words'][25]<<16) if source=='snes' else (row['words'][24]<<16|row['words'][25])


def compare(native,external,normalize_spawn):
    catalog=json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())
    pairs={int(row['snes'],16):{int(pose,16) for pose in row['md']}
           for group in ('exact_matches','pixel_art_variants') for row in catalog[group]}
    assert native.keys()==external.keys()
    cases={};total=0;common_roll=0;common_hurt=0
    for name,rows in native.items():
        other=external[name];assert len(rows)==len(other)
        differences=[];rolling=[];unpaired=[];hurt=[];hurt_differences=[]
        for index,(a,b) in enumerate(zip(rows,other)):
            assert a['pad']==b['pad']
            sa,sb=state(a,'snes'),state(b,'md')
            for field in ('x','y','vx','vy','health'):
                x,y=value(a,'snes',field),value(b,'md',field)
                if normalize_spawn and field in ('x','y'):
                    x-=value(rows[15],'snes',field);y-=value(other[15],'md',field)
                if x!=y:differences.append({'index':index,'field':field,'native':x,'md':y})
            if STATES.get(sa)!=sb:unpaired.append({'index':index,'native':sa,'md':sb})
            if sa in HURT and HURT[sa]==sb:
                hurt.append(index)
                if b['pose'] not in pairs.get(a['pose'],set()):
                    hurt_differences.append({'index':index,'field':'pose','native':a['pose'],'md':b['pose']})
                if a['words'][22]!=b['words'][22]:
                    hurt_differences.append({'index':index,'field':'timer','native':a['words'][22],'md':b['words'][22]})
            if sa in ROLL and ROLL[sa]==sb:
                assert b['pose'] in pairs.get(a['pose'],set()),(name,index,'roll pose',hex(a['pose']),hex(b['pose']))
                assert a['words'][23]==b['words'][23],(name,index,'roll counter')
                # Never hide motion differences even in a common action state.
                rolling.append(index)
        total+=len(rows);common_roll+=len(rolling);common_hurt+=len(hurt)
        gap=bool(differences or unpaired or hurt_differences)
        cases[name]={'result':'DIFFERENCES' if gap else 'MATCH', 'fields':len(rows),
                     'common_roll_fields':len(rolling),'native_roll_fields':sum(state(r,'snes') in ROLL for r in rows),
                     'md_roll_fields':sum(state(r,'md') in ROLL.values() for r in other),
                     'field_difference_counts':dict(Counter(d['field'] for d in differences)),
                     'first_differences':differences[:12], 'state_divergence_count':len(unpaired),
                     'first_state_divergences':unpaired[:8], 'common_hurt_fields':len(hurt),
                     'hurt_pose_timer_difference_count':len(hurt_differences),
                     'first_hurt_pose_timer_differences':hurt_differences[:8]}
        print(name,cases[name]['result'],'common roll fields',len(rolling),'differences',cases[name]['field_difference_counts'],flush=True)
    return {'cases':cases,'total_fields_per_version':total,'paired_roll_pose_counter_fields':common_roll,
            'paired_hurt_fields':common_hurt}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--md-start',action='store_true',help='Compare the native host with only MD initial position selected, using absolute coordinates')
    args=parser.parse_args()
    out=ROOT/'build/pride-roll-original'
    native_path=ROOT/'build/pride-roll-md-start/snes.json' if args.md_start else out/'snes.json'
    a=json.loads(native_path.read_text());b=json.loads((out/'md.json').read_text())
    assert a['settle_frames']==b['settle_frames']==256 and b['fresh_md_input_boot']
    if args.md_start:
        assert a['md_start_selected']
        report=compare(a['cases'],b['cases'],False)
        assert all(rows[15]['x']==65 and rows[15]['y']==1255 for rows in a['cases'].values())
        report.update(result='PARTIAL',scope=__doc__,initial_spawn_offset_normalized=False,
                      md_start_selected=True,whole_rolling_environment_damage_equivalence_proven=False,
                      source_sha256={'snes':hashlib.sha256(native_path.read_bytes()).hexdigest(),
                                     'md':hashlib.sha256((out/'md.json').read_bytes()).hexdigest()})
        (native_path.parent/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
        print('Absolute roll comparison indexed; contact/damage differences remain open',flush=True)
        return
    report=compare(a['cases'],b['cases'],True)
    # Record the boundary case in absolute coordinates as well: after contact
    # the two original positions converge, invalidating a constant origin shift.
    left=a['cases']['left-boundary-roll'];right=b['cases']['left-boundary-roll']
    equal=[i for i,(x,y) in enumerate(zip(left,right)) if value(x,'snes','x')==value(y,'md','x')]
    assert equal and all(value(left[i],'snes','x')==value(right[i],'md','x') for i in range(equal[0],len(left)))
    report.update(result='PARTIAL',scope=__doc__,initial_spawn_offset_normalized=True,
                  left_boundary_absolute_positions_converge_at=equal[0],
                  whole_rolling_environment_damage_equivalence_proven=False,
                  source_sha256={s:hashlib.sha256((out/(s+'.json')).read_bytes()).hexdigest() for s in ('snes','md')})
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original roll comparison indexed with all unresolved differences; full rolling behavior NOT declared complete',flush=True)


if __name__=='__main__':main()
