"""Bind the published music fix to current code, whole-game gates and OS evidence."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-music-output65';out=base/'bindings2';out.mkdir();checks={};counts={};paths=[Path(__file__)]
    names=['component','completion','lifecycle','audio-device','windows-ui','windows-visible','package-play2','native75','allbugs-verification','hyena-effects','publication','cmd-play','game-window-verification']
    for name in names:
        p=base/name/'report.json';r=bound(p);paths.append(p)
        checks[name]=r['result']=='PASS' and all(r.get('checks',{'component':'PASS' in r.get('output','')}).values())
        counts[name]=len(r.get('checks',{}))
    bp=base/'build-report.json';build=bound(bp);paths.append(bp)
    parentpath=ROOT/'build/pride-music-output62/build-report.json';parent=bound(parentpath);paths.append(parentpath)
    publicpath=ROOT/'build/pride-checkpoint-capability53/build-report.json';old=bound(publicpath);paths.append(publicpath)
    inputs=build['link_inputs_sha256']
    checks['all322_compiled_inputs_bound']=len(inputs)==322 and all(digest(ROOT/name)==sha for name,sha in inputs.items())
    checks['only_owner_changed_from62']=sum(parent['link_inputs_sha256'].get(p)==sha for p,sha in inputs.items())==321
    checks['only_three_audio_objects_changed_from53']=sum(old['link_inputs_sha256'].get(p)==sha for p,sha in inputs.items())==319
    source=ROOT/'engine/runner/tlk_native_audio_owner.c';paths.append(source)
    checks['maintained_owner_source_matches_build']=digest(source)==build['source_sha256'][source.relative_to(ROOT).as_posix()]
    checks['current_owner_schema_only']='"SEMOWN02"' in source.read_text() and '"SEMOWN01"' not in source.read_text()
    generationpath=ROOT/'build/pride-checkpoint-hooks52/generation-report.json';generation=bound(generationpath);paths.append(generationpath)
    checks['generated_guest_hooks_bound']=generation['result']=='GENERATED' and all(digest(generationpath.parent/p)==sha for p,sha in generation['generated_sha256'].items())
    echo=ROOT/'build/pride-music-observer63/verification/report.json';r=bound(echo);paths.append(echo)
    checks['zero_echo_context_evidence_and_observer_neutrality']=r['result']=='PASS' and all(r['checks'].values())
    incident=base/'historical-cache-incident/report.json';disclosure=bound(incident);paths.append(incident)
    checks['historical_cache_mutation_disclosed']=disclosure['original_cache_bytes_unrecovered'] and all(disclosure['checks'].values())
    rejected=ROOT/'build/pride-music-output62/lifecycle/report.json';r=json.loads(rejected.read_text());paths.append(rejected)
    # Original report/source identities and every unaffected primary artifact
    # are validated in the disclosure. Its overwritten auto-caches are not proof.
    checks['preceding_continue_failure_retained']=r['result']=='FAIL' and {k for k,v in r['checks'].items() if not v}=={'continue_over_whole_pcm_mode_parity','continue_all_whole_pcm_mode_parity'}
    package=ROOT/'dist/installed-preview65';packagepath=package/'package-report.json';bound(packagepath);paths.append(packagepath)
    info=json.loads((package/'package.json').read_text())
    checks['published_binary_exact']=digest(package/'LionKing.exe')==digest(base/'player.exe')==build['binary_sha256']==info['player_sha256']
    checks['backend_exact']=digest(package/'genesis_plus_gx_libretro.dll')==info['backend_sha256']
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';paths.append(launcher)
    checks['launcher_selects65']='dist/installed-preview65' in launcher.read_text()
    manifestpath=ROOT/'game-data/install.json';manifest=json.loads(manifestpath.read_text(encoding='utf-8-sig'));paths.append(manifestpath)
    payload=ROOT/'game-data'/manifest['sprite_assets']['file']
    checks['prepared_sprite_policy_exact']=digest(payload)==manifest['sprite_assets']['sha256'] and payload.read_bytes()[88:120].hex()==info['required_sprite_policy_sha256']
    beforepath=ROOT/'build/pride-checkpoint-capability53/publication/report.json';before=bound(beforepath);paths.append(beforepath)
    helper=ROOT/'dist/PrepareSpriteAssets.exe';paths.append(helper)
    checks['installed_data_and_helper_unchanged']=digest(manifestpath)==before['source_sha256'][manifestpath.relative_to(ROOT).as_posix()] and digest(helper)==before['source_sha256'][helper.relative_to(ROOT).as_posix()]
    checks['capability_does_not_claim_full_first_level']=info['full_first_level_fidelity_complete'] is False
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    visual=[base/'windows-visible/snes-gameplay.png',base/'windows-visible/md-gameplay.png',base/'game-window-verification/game.png',base/'game-window-verification/resources.png']
    paths.extend(visual)
    paths.extend(ROOT/p for p in ('engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_native_audio_owner.h','engine/cmake/runtime-patches/native_audio_owner_dsp.hunks','tools/pride_arena_history.py','Play Installed Preview.cmd'))
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,report_check_counts=counts,published=True,
                native75_current65=True,allbugs_current65_observer_fields_per_mode=60648,
                manual_os_visual_review=[p.relative_to(ROOT).as_posix() for p in visual],
                music_scope='Pride main/battle, health-death and Continue/game-over in verified zero-echo contexts',
                later_levels_retain_existing_music_transport=True,full_first_level_fidelity_complete=False,
                historical_automatic_cache_loss_disclosed=True,
                current_build_saves_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],counts,flush=True)


if __name__=='__main__':main()
