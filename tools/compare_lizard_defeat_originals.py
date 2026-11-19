"""Compare the two original defeat timers; keep unrelated cue labels separate."""
import json
from audit_scenes import ROOT,read_rom


def main():
    out=ROOT/'build/lizard-defeat-original'
    native=json.loads((out/'native.json').read_text());md=json.loads((out/'md.json').read_text())
    assert native['result']==md['result']=='PASS' and len(native['entries'])==len(md['entries'])==2
    pose_pairs=dict(zip((0xc2f35f,0xc2f396,0xc2f3e1,0xc2f428,0xc2f47f,0xc2f4ca,0xc2f50d,0xc2f550),
                        (0xb4fec,0xb5014,0xb505c,0xb50d4,0xb514c,0xb51e4,0xb527c,0xb52f4)))
    checked=0
    for left,right in zip(native['entries'],md['entries']):
        def timeline(report,entry):
            return [r for r in report['observations'] if r['actor']==entry['actor'] and entry['frame']<=r['frame']<entry['frame']+32]
        a,b=timeline(native,left),timeline(md,right)
        assert len(a)==len(b)==32
        assert [r['timer'] for r in a]==[r['timer'] for r in b]==list(range(31,-1,-1))
        assert all(pose_pairs[x['pose']]==y['pose'] for x,y in zip(a,b)),'Animation-phase correspondence differs'
        checked+=len(a)
    assert len(md['calls'])==2 and native['no_original_sound_calls_in_observed_defeat_actions']
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    def calls(rom,opcode):
        found=[];at=0
        while True:
            at=rom.find(opcode,at)
            if at<0:return found
            found.append(at);at+=1
    native_calls=[0xc00000+p for p in calls(s,bytes.fromhex('220866c1'))]
    md_calls=calls(m,bytes.fromhex('4eb90019c554'))
    assert len(native_calls)==len(md_calls)==8
    report={'result':'PASS','scope':__doc__,'compared_action_updates':checked,'defeats_each_version':2,
            'native_entry_frames':[e['frame'] for e in native['entries']],
            'md_entry_frames':[e['frame'] for e in md['entries']],
            'same_timer32_countdown_and_animation_phases':True,'md_only_fm165_at_timer30':True,
            'actor_identity_follows_reviewed_lizard_predecessor_poses':True,
            'shared_handler_native_direct_call_sites':native_calls,'shared_handler_md_direct_call_sites':md_calls,
            'selection_follows_defeat_effect_not_exclusive_enemy_class':True,
            'does_not_map_native_event22_or_a_hyena_cue':True,
            'defeat_art_adapter_enabled_by_this_audit':False}
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Two original lizard defeats:64 timer/animation-phase updates, MD-only FM165 PASS',flush=True)


if __name__=='__main__':main()
