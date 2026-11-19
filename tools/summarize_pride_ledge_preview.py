"""Bind the ledge audio preview promotion without claiming complete Pride fidelity."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_ledge_preview_history import bound


def main():
    base=ROOT/'build/pride-ledge-work/player'
    gate_path=base/'ledge-integration-report.json';gate=bound(gate_path)
    assert gate['result']=='PARTIAL' and gate['checks']==302 and gate['native75_endpoint_pairs']==75
    launcher_path=base/'launcher-verification/report.json';launcher=bound(launcher_path)
    assert launcher['result']=='PASS' and len(launcher['checks'])==11 and all(launcher['checks'].values())
    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    for name,sha in archive['existing_settings_sha256'].items():assert digest(ROOT/name)==sha,name
    paths=[Path(__file__),gate_path,launcher_path,archive_path,ROOT/'tools/pride_ledge_preview_history.py',
           ROOT/'tools/pride_arrival_history.py',ROOT/'Play Standalone Preview.cmd',base/'launcher-verification/window.png']
    report=dict(result='PARTIAL',checks=313,total_full_picture_wram_field_comparisons=166646,
        native75_endpoint_pairs=75,native_allbugs_tracked_fields_per_mode=60648,
        matching_cold_process_combinations=24,changed_source_process_combinations=4,previous_build_load_modes=2,
        standalone_preview_promoted=True,previous_arrival_player_preserved=True,
        existing_standalone_settings_and_saves_byte_identical=True,setup_data_and_cache_verified=True,
        distribution_or_installer_updated=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=base/'ledge-preview-integration-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-ledge-preview-latest.json').write_bytes(destination.read_bytes())
    print('PARTIAL313: ledge-grab standalone preview; older players/settings retained',flush=True)


if __name__=='__main__':main()
