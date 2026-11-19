"""Final published-menu binding; every prerequisite remains separately inspectable."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-output83';out=base/'bindings';out.mkdir();checks={};paths=[Path(__file__)]
    names=['route','regression','resume','windows-ui','native75','allbugs-verification','package-play','publication','cmd-play','game-window-verification','mixed-window']
    for name in names:
        p=base/name/'report.json';r=bound(p);paths.append(p)
        checks[name]=r['result']=='PASS' and all(r['checks'].values())
    proofs=[('pride-menu-output83-owner-component','PASS'),('pride-menu-output83-controller','PASS'),
            ('pride-menu-output84-isolation','PASS'),('pride-menu-audio80-originals','MENU_CUE_MEANINGS_VERIFIED'),
            ('pride-menu-spc82','NEUTRAL_MENU_SPC_OBSERVER'),('pride-menu-owner81','NEUTRAL_MENU_OWNER_OBSERVER'),
            ('pride-title-audio77','ORIGINAL_TITLE_CAPTURED'),('pride-title-native77','NATIVE_TITLE_CAPTURED'),
            ('pride-menu-audio78','MENU_CALL_PICTURES_CAPTURED'),('pride-menu-protocol79','ORIGINAL_MENU_PROTOCOL_CAPTURED')]
    for name,result in proofs:
        p=ROOT/'build'/name/'report.json';r=bound(p);paths.append(p)
        checks[name]=r['result']==result and all(r.get('checks',{'pass':True}).values())
    bp=base/'build-report.json';b=bound(bp);paths.append(bp)
    checks['all322_link_inputs_bound']=len(b['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
    checks['three_candidate80_objects_replaced']=b['unchanged_candidate80_inputs']==319
    checks['current_owner_schema3']=b['current_owner_schema']==3 and 'SEMOWN03' in (ROOT/'engine/runner/tlk_native_audio_owner.c').read_text()
    checks['real_owner_policy_in_audio_resources_owner']=all('-DTLK_NATIVE_AUDIO_OWNER_AVAILABLE=1' in b['compiles'][label] for label in ('audio','resources','owner'))
    old=ROOT/'build/pride-menu-audio80/route/report.json';r=bound(old);paths.append(old)
    checks['original80_regression_retained']=r['result']=='FAIL' and sum(not v for v in r['checks'].values())==4
    attempt=ROOT/'build/pride-menu-audio80/allbugs-observer/attempt-report.json';r=bound(attempt);paths.append(attempt)
    checks['original_observer_lookup_failure_retained']=r['result']=='FAILED_INHERITED_HOST_LOOKUP'
    package=ROOT/'dist/installed-preview83/package-report.json';bound(package);paths.append(package)
    checks['public_binary_exact']=digest(ROOT/'dist/installed-preview83/LionKing.exe')==digest(base/'player.exe')==b['binary_sha256']
    checks['shared_launcher_selects83']='dist/installed-preview83' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths += [ROOT/p for p in b['link_inputs_sha256']]
    paths += [ROOT/p for p in ['engine/runner/tlk_audio.c','engine/runner/tlk_resources.c','engine/runner/tlk_menu_audio_policy.h','engine/runner/tlk_native_audio_owner.c','engine/runner/tlk_native_audio_owner.h','engine/tests/menu_audio_test.c','scripts/RunInstalledPreview.ps1','docs/HANDOFF.md','docs/pride-menu-audio.md','docs/pride-lands-status.md','README.md','docs/launchers.md','engine/docs/devlog.md']]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published_sha256=b['binary_sha256'],
                full_first_level_complete=False,current_build_saves_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
