"""Bind the published gameplay update and its walkthrough evidence."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token-behavior50';out=base/'bindings';out.mkdir();checks={};paths=[Path(__file__)];counts={}
    scopes={name:base/name/'report.json' for name in ('pickup-approach','pickup-play','completion','behavior-ui3','native75','allbugs-verification','package-play','publication','cmd-play')}
    scopes['original_driver']=ROOT/'build/md-continue-token-driver/report.json'
    scopes['voice_duration']=ROOT/'build/md-continue-token-voice-duration/report.json'
    for name,path in scopes.items():
        report=bound(path);paths.append(path);checks[name]=report['result']=='PASS' and all(report['checks'].values());counts[name]=len(report['checks'])
    build_path=base/'build-report.json';build=bound(build_path);paths.append(build_path)
    checks['compiled_inputs_exact']=len(build['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    package=ROOT/'dist/installed-preview50';package_path=package/'package-report.json';bound(package_path);paths.append(package_path)
    info=json.loads((package/'package.json').read_text());checks['published_binary_exact']=digest(package/'LionKing.exe')==build['binary_sha256']==info['player_sha256']
    manifest_path=ROOT/'game-data/install.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'));payload=ROOT/'game-data'/manifest['sprite_assets']['file']
    checks['prepared_assets_match_policy']=digest(payload)==manifest['sprite_assets']['sha256'] and payload.read_bytes()[88:120].hex()==info['required_sprite_policy_sha256']
    checks['launcher_selects_current_build']='dist/installed-preview50' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['no_cross_build_migration']=('TLK_PRIDE_LEGACY_PROFILE_NODES' not in (ROOT/'engine/runner/pride/pride_practice_probe.c').read_text() and
        'TLK_PRIDE_LEGACY_PROFILE_NODES' not in (ROOT/'engine/runner/pride/final/pride_final_host.c').read_text())
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths += [ROOT/p for p in ('scripts/RunInstalledPreview.ps1','Play Installed Preview.cmd','engine/runner/tlk_continue_token_timing.h','engine/runner/tlk_audio.c',
        'engine/runner/pride/pride_practice_probe.c','engine/runner/pride/final/pride_final_host.c','engine/recomp/pride_final_hooks.json',
        'engine/cmake/final-frontend-patches/continue-token-timing.hunks','engine/cmake/game-patches/zz-continue-token-behavior-resource.hunks',
        'engine/cmake/game-patches/zzzz-continue-token-animation-save.hunks','tools/pride_arena_history.py')]
    paths.append(manifest_path)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,report_check_counts=counts,
                published=True,save_scope='current-build',cross_build_save_compatibility_required=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],counts,flush=True)


if __name__=='__main__':main()
