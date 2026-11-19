"""Bind published checkpoint functionality, accurate scope and walkthrough gates."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-checkpoint-capability53';runtime=ROOT/'build/pride-checkpoint-animation52'
    out=base/'bindings';out.mkdir();checks={};paths=[Path(__file__)];counts={}
    scopes={name:base/name/'report.json' for name in ('completion','windows-scope','package-qualification','publication','cmd-play','game-window-verification')}
    scopes.update({name:runtime/name/'report.json' for name in ('cadence-qualification','source-mixtures-qualification','windows-ui','native75','allbugs-verification')})
    scopes['original_timing']=ROOT/'build/pride-checkpoint-timing51-qualification/report.json'
    for name,path in scopes.items():
        report=bound(path);paths.append(path);checks[name]=report['result']=='PASS' and all(report['checks'].values());counts[name]=len(report['checks'])
    buildpath=base/'build-report.json';build=bound(buildpath);paths.append(buildpath)
    parentpath=runtime/'build-report.json';parent=bound(parentpath);paths.append(parentpath)
    generationpath=ROOT/'build/pride-checkpoint-hooks52/generation-report.json';generation=bound(generationpath);paths.append(generationpath)
    checks['generated_hook_sources_and_outputs_bound']=generation['result']=='GENERATED' and all(
        digest(generationpath.parent/name)==sha for name,sha in generation['generated_sha256'].items())
    previouspublication=ROOT/'build/pride-continue-token-behavior50/publication/report.json'
    previous=bound(previouspublication);paths.append(previouspublication)
    checks['prepared_install_manifest_and_helper_unchanged_since50']=previous['result']=='PASS'
    checks['all322_compiled_inputs_exact']=len(build['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    checks['53_only_capability_description_changed']=build['description_only_source_delta'] and build['unchanged_prior_inputs']==321 and not build['gameplay_or_renderer_logic_modified']
    before=(ROOT/'build/pride-checkpoint-animation52/game/tlk_resources.c').read_text()
    after=(ROOT/'build/pride-checkpoint-capability53/game/tlk_resources.c').read_text()
    checks['source_delta_rechecked']=before.count(build['before_line'])==1 and after==before.replace(build['before_line'],build['after_line'])
    failurepath=runtime/'animation-play/report.json';failure=bound(failurepath);paths.append(failurepath)
    checks['rejected_display_clock_assumption_retained']=failure['result']=='FAIL' and [k for k,v in failure['checks'].items() if not v]==['display_3729']
    checks['capability_discloses_retained_native_scheduling']=b'native game update scheduling retained' in (base/'player.exe').read_bytes()
    package=ROOT/'dist/installed-preview53';packagepath=package/'package-report.json';bound(packagepath);paths.append(packagepath)
    info=json.loads((package/'package.json').read_text())
    checks['published_binary_exact']=digest(package/'LionKing.exe')==build['binary_sha256']==info['player_sha256']
    manifestpath=ROOT/'game-data/install.json';manifest=json.loads(manifestpath.read_text(encoding='utf-8-sig'))
    payload=ROOT/'game-data'/manifest['sprite_assets']['file']
    checks['prepared_sprite_policy_exact']=digest(payload)==manifest['sprite_assets']['sha256'] and payload.read_bytes()[88:120].hex()==info['required_sprite_policy_sha256']
    checks['launcher_selects53']='dist/installed-preview53' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['no_cross_build_migration']=all('TLK_PRIDE_LEGACY_PROFILE_NODES' not in (ROOT/p).read_text() for p in ('engine/runner/pride/pride_practice_probe.c','engine/runner/pride/final/pride_final_host.c'))
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths += [ROOT/p for p in ('scripts/RunInstalledPreview.ps1','Play Installed Preview.cmd','engine/runner/tlk_checkpoint_timing.h',
        'engine/runner/tlk_checkpoint_role.h','engine/recomp/pride_final_hooks.json',
        'engine/cmake/final-frontend-patches/zz-checkpoint-timing.hunks','engine/cmake/game-patches/zzz-checkpoint-animation-resource.hunks',
        'tools/pride_arena_history.py')]
    paths.append(manifestpath)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,report_check_counts=counts,
                published=True,native75_allbugs_binary_scope='52 runtime;53 description-only relink with exact321 remaining inputs',
                save_scope='current-build',cross_build_save_compatibility_required=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],counts,flush=True)


if __name__=='__main__':main()
