"""Bind published hyena voice correction and explicitly retained verifier failures."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-hyena-voice72';out=base/'bindings';out.mkdir()
    paths=[Path(__file__)];checks={}
    names=('completion','native75','allbugs-verification','voice-audible','voice-resume-qualification','voice-ui','package-play2','publication','cmd-play','game-window-verification','mixed-window')
    for name in names:
        p=base/name/'report.json';r=bound(p);paths.append(p)
        checks[name]=r['result']=='PASS' and all(r['checks'].values())
    component=ROOT/'build/pride-hyena-voice72-component/report.json';c=bound(component);paths.append(component)
    checks['real_component63']=c['result']=='PASS' and c['output'].strip()=='PASS 63 checks'
    bp=base/'build-report.json';b=bound(bp);paths.append(bp)
    checks['all322_link_inputs_bound']=len(b['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
    checks['only_five_public65_objects_replaced']=b['unchanged_public65_inputs']==317
    gen=ROOT/'build/pride-hyena-voice71-generation/generation-report.json';g=bound(gen);paths.append(gen)
    checks['generated_original_program_contract_unchanged']=g['result']=='GENERATED' and g['program_contract_sha256']=='6ac162f5d788d7abb8b27808677a2f4bb5217f129d69232f3a35d58cb9cde304'
    checks['entry_policy_built_in_real_audio_and_resources']=all('-DTLK_HYENA_VOICE_ENTRY_AVAILABLE=1' in b['compiles'][label] for label in ('audio','resources'))
    oldfight=base/'voice-fight/report.json';f=bound(oldfight);paths.append(oldfight)
    checks['original_fight_failure_retained_and_narrowly_qualified']=f['result']=='FAIL' and [k for k,v in f['checks'].items() if not v]==['md_voice_audible_before_native_animation_cue']
    oldresume=base/'voice-resume/report.json';r=bound(oldresume);paths.append(oldresume)
    checks['original_resume_failure_retained_and_corrected']=r['result']=='FAIL' and sum(r['checks'].values())==23 and len(r['checks'])==43
    package=ROOT/'dist/installed-preview72/package-report.json';p=bound(package);paths.append(package)
    checks['published_binary_exact']=digest(ROOT/'dist/installed-preview72/LionKing.exe')==digest(base/'player.exe')==b['binary_sha256']
    checks['public_shared_launcher_selects72']='dist/installed-preview72' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths.extend([ROOT/name for name in b['link_inputs_sha256']])
    maintained=['engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_hyena_audio.c','engine/runner/tlk_hyena_audio.h','engine/runner/tlk_hyena_voice_policy.h','engine/runner/tlk_resources.c','engine/recomp/pride_hooks.json','engine/cmake/TlkPrideFinalPlayer.cmake','engine/cmake/final-frontend-patches/hyena-voice-entry.hunks','engine/tests/hyena_voice_entry_test.c','scripts/RunInstalledPreview.ps1','docs/pride-hyena-voice-timing.md','docs/HANDOFF.md']
    paths.extend(ROOT/name for name in maintained)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published_sha256=b['binary_sha256'],
                full_first_level_complete=False,legacy_compatibility_not_a_requirement=True,
                retained_failed_attempts=['build/pride-hyena-voice71/link.log','build/pride-hyena-voice71-component/compile.log','build/pride-hyena-voice72/voice-fight/report.json','build/pride-hyena-voice72/voice-resume/report.json','build/pride-hyena-voice72/package-play/run.log'],
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
