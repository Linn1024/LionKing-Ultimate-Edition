"""Bind published lizard voice timing to original evidence and current runtime."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-lizard-voice74';out=base/'bindings';out.mkdir()
    paths=[Path(__file__)];checks={}
    names=('completion','native75','allbugs-verification','voice-fight','voice-resume','voice-ui','hyena-regression','package-play','publication','cmd-play','game-window-qualification','mixed-window')
    for name in names:
        p=base/name/'report.json';r=bound(p);paths.append(p)
        checks[name]=r['result']=='PASS' and all(r['checks'].values())
    component=ROOT/'build/pride-lizard-voice74-component/report.json';c=bound(component);paths.append(component)
    checks['real_component273']=c['result']=='PASS' and c['output'].strip()=='PASS 273 checks'
    bp=base/'build-report.json';b=bound(bp);paths.append(bp)
    checks['all322_link_inputs_bound']=len(b['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
    checks['only_five_public72_objects_replaced']=b['unchanged_public72_inputs']==317
    gen=ROOT/'build/pride-lizard-voice74-generation/generation-report.json';g=bound(gen);paths.append(gen)
    checks['generated_original_program_contract_unchanged']=g['result']=='GENERATED' and g['program_contract_sha256']=='6ac162f5d788d7abb8b27808677a2f4bb5217f129d69232f3a35d58cb9cde304'
    checks['both_voice_policies_in_real_audio_and_resources']=all(all(flag in b['compiles'][label] for flag in ('-DTLK_HYENA_VOICE_ENTRY_AVAILABLE=1','-DTLK_LIZARD_VOICE_TIMING_AVAILABLE=1')) for label in ('audio','resources'))
    for name,result in [('pride-lizard-voice73','CONFIRMED_LIZARD_SOUND_COUNTER_DIFFERENCE'),('pride-lizard-voice73-natural','BOUNDED_NATURAL_LIZARD_VOICE_OWNERS_VERIFIED')]:
        evidence=ROOT/'build'/name/'report.json';r=bound(evidence);paths.append(evidence)
        checks[name]=r['result']==result and all(r['checks'].values())
    pytest=base/'auxiliary2/report.json';r=json.loads(pytest.read_text());paths.append(pytest)
    checks['utility_pytests23pass4skip']=r['result']=='PASS' and digest(pytest.parent/'pytest.log')==r['log_sha256'] and '23 passed, 4 skipped' in (pytest.parent/'pytest.log').read_text()
    package=ROOT/'dist/installed-preview74/package-report.json';p=bound(package);paths.append(package)
    checks['published_binary_exact']=digest(ROOT/'dist/installed-preview74/LionKing.exe')==digest(base/'player.exe')==b['binary_sha256']
    checks['public_shared_launcher_selects74']='dist/installed-preview74' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths.extend([ROOT/name for name in b['link_inputs_sha256']])
    maintained=['engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_lizard_audio.c','engine/runner/tlk_lizard_audio.h','engine/runner/tlk_lizard_voice_policy.h','engine/runner/tlk_hyena_audio.c','engine/runner/tlk_hyena_voice_policy.h','engine/runner/tlk_resources.c','engine/recomp/pride_hooks.json','engine/cmake/TlkPrideFinalPlayer.cmake','engine/cmake/final-frontend-patches/lizard-voice-timing.hunks','engine/tests/lizard_voice_entry_test.c','scripts/RunInstalledPreview.ps1','docs/pride-lizard-voice-timing.md','docs/HANDOFF.md']
    paths.extend(ROOT/name for name in maintained)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published_sha256=b['binary_sha256'],
                full_first_level_complete=False,legacy_compatibility_not_a_requirement=True,
                retained_environment_attempt='build/pride-lizard-voice74/auxiliary/report.json',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
