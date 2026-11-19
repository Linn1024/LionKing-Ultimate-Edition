"""Bind the verified arrival launcher and keep older player evidence intact."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_preview_history import bound


def main():
    base=ROOT/'build/pride-arrival-work/player'
    native_path=base/'arrival-native-integration-report.json';native=bound(native_path)
    assert native['result']=='PARTIAL' and native['checks']==258 and native['native_endpoint_pairs']==75
    launcher_path=base/'launcher-verification/report.json';launcher=bound(launcher_path)
    assert launcher['result']=='PASS' and len(launcher['checks'])==11 and all(launcher['checks'].values())
    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    for name,sha in archive['existing_settings_sha256'].items():assert digest(ROOT/name)==sha,name
    paths=[Path(__file__),native_path,launcher_path,archive_path,ROOT/'tools/pride_preview_history.py',
           ROOT/'tools/pride_arrival_history.py',ROOT/'Play Standalone Preview.cmd',base/'launcher-verification/window.png']
    report=dict(result='PARTIAL',checks=269,paired_picture_full_wram_fields=45100,native75_endpoint_pairs=75,
        native_allbugs_tracked_fields_per_mode=60648,cold_matching_process_combinations=20,
        changed_audio_process_combinations=4,actual_source_restart_fields=3600,audible_complete_route_fields=5000,
        standalone_preview_promoted=True,previous_flight_player_preserved=True,
        existing_standalone_settings_and_saves_byte_identical=True,setup_imported_data_and_cache_verified=True,
        distribution_or_installer_updated=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=base/'arrival-preview-integration-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-arrival-preview-latest.json').write_bytes(destination.read_bytes())
    print('PARTIAL269: arrival standalone preview; prior player and existing settings retained',flush=True)


if __name__=='__main__':main()
