"""Bind ordinary saves, practice restart, loaded clients and rejection evidence."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels

BASE=ROOT/'build/pride-practice'


def bound(path):
    r=json.loads(path.read_text())
    for name,sha in r.get('source_sha256',{}).items():assert digest(ROOT/name)==sha,(path,name)
    for name,sha in r.get('artifacts_sha256',{}).items():assert digest(path.parent/name)==sha,(path,name)
    return r


def main():
    build_path=BASE/'build-report.json';build=bound(build_path)
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for host,r in build['runs'].items():
        assert digest(BASE/f'practice-{host}.exe')==r['binary_sha256']
        for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    clock_path=ROOT/'build/pride-restart-clock/build-report.json';clock=bound(clock_path)
    for host in ('probe','sdl'):
        path=ROOT/'build/pride-restart-clock'/(host+'-bridge.obj');key=str(path.relative_to(ROOT)).replace('\\','/')
        assert build['runs'][host]['link_inputs_sha256'][key]==clock['runs'][host]['link_inputs_sha256'][key]==digest(path)
    paths=[Path(__file__),build_path,clock_path];reports={};checks=0
    def case(relative):
        nonlocal checks
        path=BASE/'verified'/relative/'report.json';r=bound(path)
        assert r['result']=='PASS' and all(r['checks'].values()),relative
        assert r['binary_sha256'] in [v['binary_sha256'] for v in build['runs'].values()]
        reports[relative]=digest(path);paths.append(path);checks+=len(r['checks']);return r
    for mode in ('native-aot','md-lle'):
        for route in ('ui','normal-ui'):
            r=case(route+'/'+mode)
            assert r['observations']['automatic_saved_field']==(1427 if route=='ui' else 1211)
            assert r['observations']['manual_saved_field']>r['observations']['automatic_saved_field']
        for route in ('boundary','boundary-normal'):
            r=case(route+'/'+mode)
            assert r['checks']['automatic_equals_explicit'] and r['checks']['manual_replay_pcm'] and r['checks']['restart_replay_pcm']
    for name in ('native','md','cross-frames'):case('headless-state/'+name)
    for name in ('native','md'):case('windows-auto-state/'+name)
    for n in (0,1):case('owned-saves/'+str(n))
    first_pixels=0
    for name in ('native','md'):first_pixels+=case('first-loaded/'+name)['pixels_compared']
    rejection_pixels=0
    for name in ('crc-md','backend-native'):
        r=case('rejection/'+name)
        assert len(r['loads'])==2 and r['loads'][0]['success']=='1' and r['loads'][1]['success']=='0'
        w,h,_=pixels(BASE/'verified/rejection'/name/'candidate/window.png');rejection_pixels+=w*h
    reproduction_path=ROOT/'build/pride-practice-reproduction/report.json';reproduction=bound(reproduction_path);paths.append(reproduction_path)
    assert reproduction['result']=='REPRODUCED' and not reproduction['restart_state_exists']
    paths.extend((ROOT/'tools/pride_practice_probe.c',ROOT/'tools/pride_practice_context.c',ROOT/'engine/runner/sdl_main.c',
        ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'))
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,checks_passed=checks,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        automatic_save_and_explicit_post_audio_equal_cases=4,real_f1_f5_f9_scenarios=4,
        new_process_ordinary_cases=5,existing_owned_save_cases=2,graphics_change_on_load_verified=True,
        first_loaded_and_plus8_client_pixels=first_pixels,rejected_load_notification_pixels=rejection_pixels,
        rejected_ordinary_loads_while_owned=2,native_replayed_pcm_exact=True,
        practice_restart_before_revival_verified=True,practice_restart_from_owned_revival_verified=False,
        arbitrary_loader_save_contexts_verified=False,live_source_restart_verified=False,md_audio_restart_verified=False,
        mixed_ui_overlay_fidelity_complete=False,
        known_mixed_ui_issue='ComposeWide copies panels tinted against native pixels; long notifications can imprint native HUD in MD output.',
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-practice-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL ordinary/practice:',len(reports),'passing reports;',checks,'checks;',first_pixels,'first-loaded client pixels',flush=True)


if __name__=='__main__':main()
