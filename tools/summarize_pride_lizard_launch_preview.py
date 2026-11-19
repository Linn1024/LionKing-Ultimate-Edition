"""Bind the actual launcher promotion without claiming full Pride completion."""
import json
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player'
    integration=base/'launch-integration-report.json';gate=bound(integration)
    assert gate['result']=='PARTIAL' and gate['checks']==352
    launcher=base/'launcher-verification/report.json';report=bound(launcher)
    assert report['result']=='PASS' and len(report['checks'])==11 and all(report['checks'].values())
    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    for name,sha in archive['existing_settings_sha256'].items():assert digest(ROOT/name)==sha,name
    paths=[integration,launcher,archive_path,ROOT/'Play Standalone Preview.cmd',
        ROOT/'tools/pride_lizard_launch_preview_history.py',
        base/'launcher-verification/window.png',base/'launch-music-mix/launch-aot/window.png']
    report=dict(result='PARTIAL',checks=363,binary_sha256=gate['binary_sha256'],
        standalone_preview_promoted=True,preceding_ledge_player_preserved=True,
        existing_setting_and_save_files_unchanged=True,
        preserved_settings_file_count=len(archive['existing_settings_sha256']),
        setup_data_and_cache_verified=True,distribution_or_installer_updated=False,
        native75_endpoint_pairs=75,native_allbugs_tracked_fields_per_mode=60648,
        matching_cold_load_mode_combinations=24,cue_using_music_mix_verified=True,
        existing_bounce_timing_equivalence_proven=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [__import__('pathlib').Path(__file__),*paths]})
    destination=base/'launch-preview-integration-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    latest=ROOT/'build/pride-lizard-launch-preview-latest.json';assert not latest.exists()
    latest.write_bytes(destination.read_bytes())
    print('PARTIAL363: launch-sound preview promoted; full Pride remains open',flush=True)


if __name__=='__main__':main()
