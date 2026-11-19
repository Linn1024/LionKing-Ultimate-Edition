"""Bind prepared HUD extraction, fresh playback, packaging and the usable launcher."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-hud-fresh43'
    out = base/'bindings'; out.mkdir()
    paths = [Path(__file__)]
    checks = {}
    scopes = [
        ('component', ROOT/'build/pride-hud-assets/verification/report.json', 1247),
        ('setup', ROOT/'build/pride-hud-assets/setup-verification/report.json', 16),
        ('setup_window', ROOT/'build/pride-hud-assets/window/report.json', 10),
        ('integrated_runtime', ROOT/'build/pride-hud-assets42/runtime-verification/report.json', 97),
        ('integrated_saves', ROOT/'build/pride-hud-assets42/setup-verification/report.json', 31),
        ('fresh_runtime', base/'runtime-verification/report.json', 97),
        ('fresh_saves', base/'setup-verification/report.json', 31),
        ('continue', base/'continue-verification/report.json', 32),
        ('native75', base/'native75/report.json', 302),
        ('allbugs', base/'allbugs-verification/report.json', 13),
        ('fresh_preparer', base/'preparer-verification/report.json', 2),
        ('package', base/'package-verification/report.json', 15),
        ('launcher_window', base/'window-verification/report.json', 6),
        ('default_installation', ROOT/'build/pride-hud-default-install/report.json', 4)]
    for label, path, count in scopes:
        report = bound(path); paths.append(path)
        checks[label] = report['result'] == 'PASS' and len(report['checks']) == count and all(report['checks'].values())
        if label == 'package':
            checks['all_packaged_files_unchanged'] = all(digest(ROOT/p) == sha for p, sha in report['package_files_sha256'].items())
        if label == 'default_installation':
            checks['existing_user_files_still_preserved'] = all(digest(ROOT/p) == sha for p, sha in report['preserved_files_sha256'].items())
    fresh_path = base/'build-report.json'; fresh = bound(fresh_path); paths.append(fresh_path)
    checks['all322_inputs_fresh_and_bound'] = (fresh['fresh_standalone_graph_claimed']
        and not fresh['old_objects_or_archives_imported'] and len(fresh['link_inputs_sha256']) == 322
        and all((ROOT/p).is_relative_to(base) and digest(ROOT/p) == sha for p, sha in fresh['link_inputs_sha256'].items()))
    package = ROOT/'dist/installed-preview43'
    checks['published_preview_binary_exact'] = digest(package/'LionKing.exe') == digest(base/'player.exe') == fresh['binary_sha256']
    failed_path = base/'launcher-verification/report.json'; failed = bound(failed_path); paths.append(failed_path)
    checks['false_markdown_classification_retained'] = failed['result'] == 'FAIL' and sum(failed['checks'].values()) == 13
    default = base/'default-cmd-verification'
    checks['actual_default_data_cmd_launch'] = ((default/'window.png').exists() and
        'resource_cache=loaded' in (default/'settings/last-launch.log').read_text())
    checks['previous_preview_unchanged'] = digest(ROOT/'build/pride-cold-boot2/player.exe') == 'dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['previous_launcher_unchanged'] = digest(ROOT/'Play Standalone Preview.cmd') == 'c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['previous_preparation_helper_unchanged'] = digest(ROOT/'dist/PrepareFinalAssets.exe') == '1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['hud_helper_available_to_setup'] = digest(ROOT/'dist/PrepareHudAssets.exe') == '5053311849a9388640398186344d16f0ee20a6bc1537ab02cf7b45414a612dc7'
    checks['frameworks_unmodified'] = not subprocess.check_output(
        ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT/'engine').strip()
    paths += [ROOT/'scripts/Setup.ps1', ROOT/'scripts/Build.ps1', ROOT/'scripts/RunInstalledPreview.ps1',
              ROOT/'Play Installed Preview.cmd', ROOT/'tools/package_pride_installed_preview.py',
              ROOT/'engine/runner/tlk_md_hud_assets.c', ROOT/'engine/runner/tlk_md_hud_prepare.c',
              ROOT/'engine/runner/tlk_md_hud_assets.h', ROOT/'engine/runner/tlk_md_hud_assets_internal.h',
              ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake', ROOT/'engine/cmake/TlkHudAssets.cmake']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  full_first_level_fidelity_complete=False, remaining_sprite_and_resource_installation_migration=True,
                  additional_launcher_published=True, existing_preview_preserved=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
