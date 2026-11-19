"""Bind the real local launcher update and preserve the full unfinished goal."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_preview_history import bound


def main():
    base=ROOT/'build/pride-bounce-owner-work/player'
    integration=base/'ownership-integration-report.json';r=bound(integration)
    assert r['result']=='PARTIAL' and r['checks']==313
    for name in ('verification','saves','legacy-source','invalid-saves','timed-load2',
                 'allbugs-standalone','bounce-music-mix','bounce-pause','bounce-restart',
                 'audio-device','regression','width-completion'):
        assert bound(base/name/'report.json')['result']=='PASS'
    launcher=base/'launcher-verification2/report.json';gate=bound(launcher)
    assert gate['result']=='PASS' and len(gate['checks'])==11 and all(gate['checks'].values())
    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    for name,sha in archive['existing_settings_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(base/'native-engine/tlk_pride_player.exe')==r['binary_sha256']
    paths=[Path(__file__),integration,launcher,archive_path,ROOT/'Play Standalone Preview.cmd',
        ROOT/'tools/pride_bounce_owner_preview_history.py',base/'launcher-verification/report.json',
        base/'launcher-verification2/window.png',base/'width-completion/aot/window.png']
    report=dict(result='PARTIAL',checks=324,binary_sha256=r['binary_sha256'],
        standalone_preview_promoted=True,maintained_native_ownership_repair_verified=True,
        preceding_lizard_player_preserved=True,existing_setting_and_save_files_unchanged=True,
        preserved_settings_file_count=len(archive['existing_settings_sha256']),
        setup_data_and_cache_verified=True,distribution_or_installer_updated=False,
        native75_endpoint_pairs=75,native_allbugs_tracked_fields_per_mode=60648,
        cold_load_mode_combinations=8,wasapi_output_verified=True,
        supported_mixed_completion_verified=True,complete_static_proof=False,
        static_wrong=0,static_unproven=11,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=base/'ownership-preview-integration-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    latest=ROOT/'build/pride-bounce-owner-preview-latest.json';assert not latest.exists()
    latest.write_bytes(destination.read_bytes())
    print('PARTIAL324: maintained ownership preview promoted; full Pride scope open',flush=True)


if __name__=='__main__':main()
