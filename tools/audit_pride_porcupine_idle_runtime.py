"""Bind shared original idle rule to real callers, live entry, cues and cold saves."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-idle-bindings';out.mkdir();checks={}
    paths=[ROOT/'build/pride-porcupine-idle/report.json',ROOT/'build/md-porcupine-idle-roar/report.json',
        ROOT/'build/md-porcupine-idle-roar2/report.json',ROOT/'build/pride-porcupine-idle-runtime/report.json',
        ROOT/'build/pride-porcupine-idle-calls/report.json',ROOT/'build/md-porcupine-idle-response-view/report.json',
        ROOT/'build/md-porcupine-idle-response-view2/report.json',ROOT/'build/pride-porcupine-idle-roar/report.json',
        ROOT/'build/pride-porcupine-idle-roar2/report.json']
    oracle,rejected,original,live,calls,walking_view,idle_view,initial_port,port=[bound(p) for p in paths]
    checks['31713_paired_original_fixtures']=oracle['result']=='PASS' and len(oracle['checks'])==31713 and all(oracle['checks'].values())
    checks['no_original_callee_intercepts']=oracle['intercepted_callees']==[]
    checks['live36']=live['result']=='PASS' and len(live['checks'])==36 and all(live['checks'].values())
    checks['direct_original_calls9']=calls['result']=='PASS' and len(calls['checks'])==9 and all(calls['checks'].values())
    checks['correct_original_idle_view2']=idle_view['result']=='PASS' and all(idle_view['checks'].values())
    checks['walking_postcall_expectation_retained']=walking_view['result']=='FAIL' and walking_view['checks']['original_observation_reproduced'] and walking_view['entry']['timer']==27 and walking_view['entry']['script']=='0xb8750'
    checks['actual_original_idle_caller']=any(r['actor']=='9a4e' and r['action']=='19a128' for r in original['cases']['3280-56']['idle_helpers'])
    decision_rows=[]
    for phase,data in [('initial',rejected),('upgraded',original)]:
        for name,case in data['cases'].items():
            for r in case['idle_helpers']:
                distance=max(abs(int(r['player_x'])-int(r['actor_x'])),abs(int(r['player_y'])-int(r['actor_y'])))
                effective=int(r['roar_active'])-max(0,distance-50)//8
                installed=any(x['actor']==r['actor'] and x['field']==r['field'] for x in case['installed'])
                decision_rows.append(dict(phase=phase,case=name,actor=r['actor'],caller_action=r['action'],distance=distance,effective=effective,installed=installed,matches=installed==(effective>10)))
    checks['all16_natural_decisions_match_rule']=len(decision_rows)==16 and all(r['matches'] for r in decision_rows)
    checks['natural_success_and_rejection']=any(r['installed'] for r in decision_rows) and any(not r['installed'] for r in decision_rows)
    checks['original_six_installations']=sum(len(c['installed']) for c in original['cases'].values())==6
    checks['original_both_facing_installations']={r['facing'] for c in original['cases'].values() for r in c['installed']}=={'0','1'}
    checks['port_three_roar_entries']=port['result']=='OBSERVED_LATE_ENTRY' and all(any(r['timer']=='28' and r['player_action']=='c3589c' for r in c['first_attack_by_actor'].values()) for c in port['cases'].values())
    checks['initial_port_negative_retained']=initial_port['result']=='NO_LATE_ENTRY_FOUND'
    base=ROOT/'build/pride-porcupine38';build_path=base/'build-report.json';paths.append(build_path);build=bound(build_path)
    checks['production_unchanged_321_inputs']=len(build['link_inputs_sha256'])==321 and digest(base/'player.exe')==build['binary_sha256'] and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    for key,path in [('snes',ROOT/'Lion King, The (USA).sfc'),('md',ROOT/'Lion King, The (World).md')]:checks[key+'_rom_identity']=digest(path)==oracle['rom_sha256'][key]
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths.append(Path(__file__))
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,natural_decisions=decision_rows,
        walking_caller_after_roar_still_requires_verification=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
