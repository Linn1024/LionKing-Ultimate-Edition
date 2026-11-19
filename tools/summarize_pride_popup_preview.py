"""Bind the actual promoted popup preview and retained user data."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_popup_preview_history import bound


def main():
    base=ROOT/'build/pride-popup-work'
    component_path=base/'candidate-report.json';component=bound(component_path)
    launcher_path=base/'launcher-verification/report.json';launcher=bound(launcher_path)
    archive_path=base/'player/launcher-baseline/report.json';archive=bound(archive_path)
    native_path=base/'native-gates/play-report.json';native=json.loads(native_path.read_text())
    assert native['result']=='PASS' and native['route_count']==75
    assert native['binary_sha256']==component['binary_sha256']
    assert launcher['result']=='PASS' and all(launcher['checks'].values())
    assert digest(ROOT/component['binary'])==component['binary_sha256']
    assert all(digest(ROOT/name)==sha for name,sha in archive['existing_settings_sha256'].items())
    paths=[Path(__file__),component_path,launcher_path,archive_path,native_path,
           ROOT/'Play Standalone Preview.cmd',ROOT/'tools/pride_popup_preview_history.py']
    result=dict(result='PARTIAL',standalone_preview_promoted=True,
                binary=component['binary'],binary_sha256=component['binary_sha256'],
                pickup_arrival_artwork_palette_position_verified=True,
                component_checks=component['verified_component_checks'],
                native_endpoint_pairs=75,launcher_checks=len(launcher['checks']),
                existing_settings_and_saves_unchanged=True,
                preceding_player_and_launcher_retained=True,
                installer_or_distribution_changed=False,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    dest=base/'preview-report.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
    latest=ROOT/'build/pride-popup-preview-latest.json';assert not latest.exists();latest.write_bytes(dest.read_bytes())
    print('Verified popup preview promoted; full Pride fidelity remains open',flush=True)


if __name__=='__main__':main()
