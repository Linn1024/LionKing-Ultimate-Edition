"""Bind prepared sprites, installation, real playback and the packaged preview."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-sprite-fresh44'
    out = base/'bindings'; out.mkdir()
    paths = [Path(__file__)]
    checks = {}
    scopes = [
        ('component', ROOT/'build/pride-sprite-assets/verification/report.json'),
        ('preparer', ROOT/'build/pride-sprite-assets/preparer-verification/report.json'),
        ('setup', ROOT/'build/pride-sprite-assets/setup-verification2/report.json'),
        ('runtime', base/'runtime-verification/report.json'),
        ('saves', base/'setup-verification/report.json'),
        ('continue', base/'continue-verification/report.json'),
        ('native75', base/'native75/report.json'),
        ('allbugs', base/'allbugs-verification/report.json'),
        ('integrated_preparer', base/'integrated-preparer/report.json'),
        ('package', base/'launcher-verification/report.json'),
        ('window', base/'window-verification/report.json'),
        ('default_install', ROOT/'build/pride-sprite-default-install/report.json'),
        ('previous_package', ROOT/'build/pride-hud-fresh43/package-verification/report.json'),
        ('previous43', ROOT/'build/pride-hud-fresh43/bindings/report.json')]
    counts = {}
    for label, path in scopes:
        report = bound(path); paths.append(path)
        checks[label] = report['result'] == 'PASS' and all(report['checks'].values())
        counts[label] = len(report['checks'])
        if label == 'default_install':
            checks['previous_user_data_preserved'] = all(digest(ROOT/p) == sha for p, sha in report['preserved_files_sha256'].items())
        if label == 'previous_package':
            checks['previous_package_files_preserved'] = all(digest(ROOT/p) == sha for p, sha in report['package_files_sha256'].items())
    fresh_path = base/'build-report.json'; fresh = bound(fresh_path); paths.append(fresh_path)
    checks['all322_inputs_fresh_and_bound'] = (fresh['fresh_standalone_graph_claimed']
        and not fresh['old_objects_or_archives_imported'] and len(fresh['link_inputs_sha256']) == 322
        and all((ROOT/p).is_relative_to(base) and digest(ROOT/p) == sha for p, sha in fresh['link_inputs_sha256'].items()))
    package = ROOT/'dist/installed-preview44'
    package_path = package/'package-report.json'; bound(package_path); paths.append(package_path)
    checks['published_binary_exact'] = digest(package/'LionKing.exe') == digest(base/'player.exe') == fresh['binary_sha256']
    checks['distributed_preparer_bound'] = digest(ROOT/'dist/PrepareSpriteAssets.exe') == '2193f1f56af19fe990aabec1375eeef8f8aa066481244a71135b5c854475c63f'
    checks['frameworks_unmodified'] = not subprocess.check_output(
        ['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT/'engine').strip()
    paths += [ROOT/'scripts/Setup.ps1', ROOT/'scripts/Build.ps1', ROOT/'scripts/RunInstalledPreview.ps1',
              ROOT/'Play Installed Preview.cmd', ROOT/'tools/package_pride_sprite_preview.py',
              ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake', ROOT/'engine/cmake/TlkSpriteAssets.cmake',
              ROOT/'engine/tools/prepare_sprite_assets.c', ROOT/'tools/pride_arena_history.py']
    paths += list((ROOT/'engine/runner').glob('tlk_md_sprite_*'))
    paths += [ROOT/'engine/cmake/game-patches/installed-sprite-payload.hunks',
              ROOT/'engine/cmake/game-patches/zzzzz-installed-sprite-resource.hunks',
              ROOT/'engine/cmake/final-frontend-patches/zzzzz-installed-sprite.hunks']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, report_check_counts=counts,
                  full_first_level_fidelity_complete=False, whole_installation_migration_complete=False,
                  new_renderer_coverage_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), counts, flush=True)


if __name__ == '__main__': main()
