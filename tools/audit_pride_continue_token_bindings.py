"""Bind published47 and the exact original/installed/runtime evidence."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token47';out=base/'bindings';out.mkdir();paths=[Path(__file__)];checks={};counts={}
    scopes={
        'effect_inventory':ROOT/'build/pride-effect-coverage/report.json',
        'dynamic_packets':ROOT/'build/pride-effect-coverage/dynamic-packets2/qualification/report.json',
        'sun_owners':ROOT/'build/pride-effect-coverage/sun-owners2/report.json',
        'map':ROOT/'build/pride-continue-token-map/report.json',
        'component':ROOT/'build/pride-continue-token46/component/report.json',
        'setup':ROOT/'build/pride-continue-token-assets/setup-verification/report.json',
        'runtime':base/'artwork-verification/report.json',
        'guards':base/'guards/report.json',
        'full_route':base/'full-route/qualification/report.json',
        'live_ui':base/'live-ui/report.json',
        'native75':base/'native75/report.json',
        'allbugs':base/'allbugs-verification/report.json',
        'legacy_continue':base/'legacy-continue/report.json',
        'launcher':base/'launcher-verification/report.json',
        'publication':base/'publication/report.json',
        'cmd':base/'cmd-verification2/report.json',
        'published_window':base/'game-window-verification/report.json',
        'original_source':ROOT/'build/pride-continue-token-source-audit/report.json',
        'original_md_phases':ROOT/'build/md-continue-token-original2/report.json',
        'original_md_neutrality':ROOT/'build/md-continue-token-original2/qualification/report.json',
        'original_md_contact':ROOT/'build/md-continue-token-contact/report.json',
        'previous44':ROOT/'build/pride-sprite-fresh44/bindings/report.json'}
    reports={}
    for label,path in scopes.items():
        data=bound(path);paths.append(path);checks[label]=data['result']=='PASS' and all(data['checks'].values());counts[label]=len(data['checks']);reports[label]=data
    build_path=base/'build-report.json';build=bound(build_path);paths.append(build_path)
    checks['all322_inputs_exact']=len(build['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    package=ROOT/'dist/installed-preview47';package_path=package/'package-report.json';bound(package_path);paths.append(package_path)
    info=json.loads((package/'package.json').read_text())
    checks['published_binary_exact']=digest(package/'LionKing.exe')==digest(base/'player.exe')==build['binary_sha256']==info['player_sha256']
    assets_path=ROOT/'build/pride-continue-token-assets/build-report.json';assets=bound(assets_path);paths.append(assets_path)
    checks['distributed_helper_exact']=digest(ROOT/'dist/PrepareSpriteAssets.exe')==assets['binary_sha256']
    data=ROOT/'game-data';manifest=json.loads((data/'install.json').read_text(encoding='utf-8-sig'));payload=data/manifest['sprite_assets']['file']
    checks['installed_policy_and_payload_exact']=digest(payload)==manifest['sprite_assets']['sha256']==assets['package_sha256'] and payload.read_bytes()[88:120].hex()==info['required_sprite_policy_sha256']
    checks['old_data_settings_and_saves_preserved']=all(digest(ROOT/p)==sha for p,sha in reports['publication']['preserved_files_sha256'].items())
    old=ROOT/'dist/installed-preview44/package-report.json';bound(old);paths.append(old)
    old_build=ROOT/'build/pride-sprite-fresh44/build-report.json';old_binary=bound(old_build)['binary_sha256'];paths.append(old_build)
    checks['previous44_package_preserved']=digest(old.parent/'LionKing.exe')==json.loads((old.parent/'package.json').read_text())['player_sha256']==old_binary
    checks['public_launcher_selects47']='dist/installed-preview47' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['resource_tree_append_only']=len(reports['published_window']['tree']['choices'])==128 and reports['published_window']['tree']['choices'][125][0]=='graphics.sprites.pickups.continue_token'
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    failures=[ROOT/'build/pride-continue-token46/artwork-verification/failure.json',base/'cmd-verification/failure.json',base/'public-window-syntax-attempt/failure.json']
    checks['failed_attempts_retained']=all(bound(path)['result']=='FAIL' for path in failures);paths+=failures
    paths += [ROOT/name for name in ('scripts/RunInstalledPreview.ps1','Play Installed Preview.cmd','scripts/Setup.ps1','dist/PrepareSpriteAssets.exe','game-data/install.json','tools/pride_arena_history.py',
        'engine/runner/tlk_continue_token_role.h','engine/runner/tlk_md_sprites.h','engine/runner/tlk_md_sprites.c','engine/runner/tlk_wide.c',
        'engine/runner/pride/pride_practice_probe.c','engine/runner/pride/final/pride_final_host.c','engine/cmake/game-patches/z-continue-token-resource.hunks',
        'tools/pride_sprite_catalog.py','tools/pride_npc_pairs.json','engine/generated/resources/pride_sprite_map.h')]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,report_check_counts=counts,published=True,
                full_first_level_complete=False,animation_reward_and_cue_remain_native=True,new_background_coverage_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],counts,flush=True)


if __name__=='__main__':main()
