"""Bind the launcher promotion without replacing historical player evidence."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-flight-player'
    renderer_path=base/'native-integration-report.json';renderer=bound(renderer_path)
    assert renderer['result']=='PARTIAL' and renderer['new_checks']==116
    assert renderer['native75_endpoint_pairs']==75 and not renderer['native75_gate_pending']
    launcher_path=base/'launcher-verification/report.json';launcher=bound(launcher_path)
    assert launcher['result']=='PASS' and len(launcher['checks'])==10 and all(launcher['checks'].values())
    assert launcher['installed_cache_used']
    archive_path=base/'launcher-baseline/report.json';archive=bound(archive_path)
    assert digest(ROOT/archive['archived_launcher'])==archive['original_launcher_sha256']
    assert digest(ROOT/'build/pride-player/player.exe')==archive['old_player_sha256']
    for name,sha in archive['existing_settings_sha256'].items():assert digest(ROOT/name)==sha,name
    paths=[Path(__file__),renderer_path,launcher_path,archive_path,ROOT/'Play Standalone Preview.cmd',
        base/'launcher-verification/window.png',ROOT/'build/pride-player/player.exe']
    report=dict(result='PARTIAL',new_checks=126,paired_picture_full_wram_fields=18124,
        semantic_predicate_checks=480,native75_endpoint_pairs=75,native_allbugs_tracked_fields_per_mode=60648,
        standalone_launcher_updated=True,previous_standalone_executable_preserved=True,
        existing_standalone_settings_and_saves_byte_identical=True,
        setup_imported_data_and_cache_verified=True,published_distribution_replaced=False,
        installer_updated=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=base/'preview-integration-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-flight-preview-latest.json').write_bytes(destination.read_bytes())
    print('PARTIAL126; standalone preview updated, existing settings/saves preserved',flush=True)


if __name__=='__main__':main()
