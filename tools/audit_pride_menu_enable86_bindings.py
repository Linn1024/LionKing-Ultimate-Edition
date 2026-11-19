"""Bind the final published build, original Off/On, and all independent source gates."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-enable86';out=base/'bindings';out.mkdir();checks={};paths=[Path(__file__)]
    names=['route','regression','enable','windows-ui','native75','allbugs-verification','package-play','publication','cmd-play','game-window-verification2','mixed-window']
    for name in names:
        p=base/name/'report.json';r=bound(p);paths.append(p)
        checks[name]=r['result']=='PASS' and all(r['checks'].values())
    proofs=[('pride-menu-enable86-owner-component','PASS'),('pride-menu-output83-controller','PASS'),
            ('pride-menu-enable86-isolation','PASS'),('pride-menu-audio80-originals','MENU_CUE_MEANINGS_VERIFIED'),
            ('pride-menu-enable85-md2','ORIGINAL_EFFECTS_ENABLE_CAPTURED'),('pride-menu-enable86-observer','NEUTRAL_ENABLE_TRANSITION_OBSERVED'),
            ('pride-menu-spc82','NEUTRAL_MENU_SPC_OBSERVER'),('pride-menu-owner81','NEUTRAL_MENU_OWNER_OBSERVER'),
            ('pride-title-audio77','ORIGINAL_TITLE_CAPTURED'),('pride-title-native77','NATIVE_TITLE_CAPTURED'),
            ('pride-menu-audio78','MENU_CALL_PICTURES_CAPTURED'),('pride-menu-protocol79','ORIGINAL_MENU_PROTOCOL_CAPTURED')]
    for name,result in proofs:
        p=ROOT/'build'/name/'report.json';r=bound(p);paths.append(p)
        checks[name]=r['result']==result and all(r.get('checks',{'pass':True}).values())
    bp=base/'build-report.json';b=bound(bp);paths.append(bp)
    checks['all322_link_inputs_bound']=len(b['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
    checks['one_candidate83_object_replaced']=b['unchanged_candidate83_inputs']==321
    checks['current_owner_schema3']=b['current_owner_schema']==3 and 'SEMOWN03' in (ROOT/'engine/runner/tlk_native_audio_owner.c').read_text()
    checks['owner_available_in_actual_audio_resources_owner']=all('-DTLK_NATIVE_AUDIO_OWNER_AVAILABLE=1' in b['compiles'][label] for label in ('audio','resources','owner'))
    for name in ('pride-menu-audio80/route','pride-menu-enable85','pride-menu-enable85-md'):
        p=ROOT/'build'/name/'report.json';r=bound(p);paths.append(p)
        checks[name+'_original_failure_retained']=r['result']=='FAIL'
    p=ROOT/'build/pride-menu-audio80/allbugs-observer/attempt-report.json';r=bound(p);paths.append(p)
    checks['original_observer_lookup_failure_retained']=r['result']=='FAILED_INHERITED_HOST_LOOKUP'
    p=base/'game-window-verification/attempt-report.json';r=bound(p);paths.append(p)
    checks['legacy_window_settings_failure_retained']=r['result']=='FAILED_LEGACY_SETTINGS_PATH_BEFORE_PLAYER_LAUNCH' and not r['player_launched']
    package=ROOT/'dist/installed-preview86/package-report.json';bound(package);paths.append(package)
    checks['public_binary_exact']=digest(ROOT/'dist/installed-preview86/LionKing.exe')==digest(base/'player.exe')==b['binary_sha256']
    checks['shared_launcher_selects86']='dist/installed-preview86' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths += [ROOT/p for p in b['link_inputs_sha256']]
    paths += [ROOT/p for p in ['engine/runner/tlk_audio.c','engine/runner/tlk_resources.c','engine/runner/tlk_menu_audio_policy.h','engine/runner/tlk_native_audio_owner.c','engine/runner/tlk_native_audio_owner.h','engine/tests/menu_audio_test.c','scripts/RunInstalledPreview.ps1','docs/HANDOFF.md','docs/pride-menu-audio.md','docs/pride-lands-status.md','README.md','docs/launchers.md','engine/docs/devlog.md']]
    # Include every live wrapper/template used for this publication, including
    # inherited source files whose exec expansion does not add itself to reports.
    paths += [p for p in (ROOT/'tools').glob('*pride_menu*.py')]
    paths += [ROOT/'tools'/p for p in ['verify_pride_checkpoint_package53.py','verify_pride_checkpoint_cmd53.py','verify_pride_checkpoint_public_window53.py','capture_pride_mixed_launcher66.py','verify_pride_music_ui65.py','verify_pride_checkpoint52_allbugs.py','build_pride_checkpoint52_allbugs.py','verify_pride_hyena_voice72_native75.py','verify_pride_installed_native75.py','menu_output_stats84.c','menu_enable_state_probe86.c','native_menu_spc_trace82.h']]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published_sha256=b['binary_sha256'],
                full_first_level_complete=False,current_build_saves_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
