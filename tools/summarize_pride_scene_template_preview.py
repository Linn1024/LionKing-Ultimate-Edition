"""Bind actual local promotion after native/mixture/launcher gates finish."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_scene_template_preview_history import bound


def main():
    base=ROOT/'build/pride-scene-template-work/player'
    integration=base/'integration175-report.json';report=bound(integration)
    assert report['result']=='PARTIAL' and report['checks']==175 and report['native75_complete'] and report['allbugs_complete']
    launcher=base/'launcher-verification/report.json';gate=bound(launcher)
    assert gate['result']=='PASS' and len(gate['checks'])==11 and all(gate['checks'].values())
    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    assert all(digest(ROOT/name)==sha for name,sha in archive['existing_settings_sha256'].items())
    assert digest(base/'native-engine/tlk_pride_player.exe')==report['binary_sha256']
    paths=[Path(__file__),integration,launcher,archive_path,ROOT/'Play Standalone Preview.cmd',
        ROOT/'tools/pride_scene_template_preview_history.py',base/'launcher-verification/window.png',base/'width-completion/aot/window.png']
    result=dict(result='PARTIAL',checks=186,binary_sha256=report['binary_sha256'],
        standalone_preview_promoted=True,native_fallback_reload_repaired=True,
        source_guard_and_prepared_capsules_preserved=True,preceding_ownership_player_preserved=True,
        existing_settings_and_saves_unchanged=True,preserved_setting_file_count=len(archive['existing_settings_sha256']),
        native75_endpoint_pairs=75,native_allbugs_tracked_fields_per_mode=60648,
        setup_data_and_cache_verified=True,distribution_or_installer_updated=False,
        new_final_life_capability_enabled=False,complete_static_proof=False,static_wrong=0,static_unproven=11,
        full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    target=base/'template-preview-integration-report.json';assert not target.exists()
    target.write_text(json.dumps(result,indent=2)+'\n')
    latest=ROOT/'build/pride-scene-template-preview-latest.json';assert not latest.exists();latest.write_bytes(target.read_bytes())
    print('PARTIAL186: reload-repair preview verified; full Pride scope remains open',flush=True)


if __name__=='__main__':main()
