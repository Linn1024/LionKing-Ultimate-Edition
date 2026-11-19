"""Package the verified fresh graph without ROMs or extracted game assets."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-continue-token47'
    build_path = base/'build-report.json'; build = bound(build_path)
    evidence = [base/folder/'report.json' for folder in
                ('artwork-verification', 'guards', 'full-route/qualification', 'native75', 'allbugs-verification', 'live-ui')]
    evidence += [ROOT/'build/pride-continue-token46/component/report.json', ROOT/'build/pride-continue-token-assets/setup-verification/report.json']
    for path in evidence:
        data = bound(path)
        assert data['result'] == 'PASS' and all(data['checks'].values()), path
    out = ROOT/'dist/installed-preview47'
    out.mkdir()
    sources = [(base/'player.exe', 'LionKing.exe'),
               (base/'genesis_plus_gx_libretro.dll', 'genesis_plus_gx_libretro.dll'),
               (base/'save-contract.json', 'save-contract.json'),
               (ROOT/'engine/LICENSE', 'licenses/LICENSE-port.txt'),
               (ROOT/'engine/snesrecomp/LICENSE', 'licenses/LICENSE-snesrecomp.txt'),
               (ROOT/'engine/recomp-ui/LICENSE', 'licenses/LICENSE-ui.txt'),
               (ROOT/'.tools/SDL3-3.4.10/LICENSE.txt', 'licenses/LICENSE-SDL3.txt'),
               (ROOT/'.tools/genesis-plus-gx/LICENSE.txt', 'licenses/LICENSE-md-backend.txt'),
               (ROOT/'engine/packaging/LICENSE-NOTES.txt', 'LICENSE-NOTES.txt'),
               (ROOT/'dist/source/Genesis-Plus-GX-source.zip', 'source/Genesis-Plus-GX-source.zip'),
               (ROOT/'engine/recomp-ui/assets/common/fonts/LatoLatin-Regular.ttf', 'assets/fonts/LatoLatin-Regular.ttf'),
               (ROOT/'engine/recomp-ui/assets/common/fonts/NOTICE.md', 'licenses/NOTICE-fonts.md')]
    for source, name in sources:
        target = out/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    shaders = ROOT/'dist/assets/shaders'
    if shaders.exists(): shutil.copytree(shaders, out/'assets/shaders')
    info = dict(schema=1, player_sha256=digest(out/'LionKing.exe'),
                backend_sha256=digest(out/'genesis_plus_gx_libretro.dll'),
                required_packages=dict(scene_cache=1, menu_assets=2, native_final_assets=2, title_bank_assets=1, hud_assets=1, sprite_assets=1),
                required_sprite_policy_sha256=(ROOT/'build/pride-continue-token-assets/sprites.assets').read_bytes()[88:120].hex(),
                full_first_level_fidelity_complete=False)
    (out/'package.json').write_text(json.dumps(info, indent=2)+'\n')
    (out/'README.txt').write_text('Installed Lion King development preview\n\nRun Setup.cmd, then Play Installed Preview.cmd from the project root.\nF12 opens the SNES/Mega Drive resource tree. This preview uses separate\nsettings/installed-preview settings and recordings. Existing previews remain\navailable. Missing or damaged prepared data requires Setup repair.\n\nThis is a hybrid using compiled game code and emulation. Scenes, HUD, mapped sprites/shared palettes and\nreviewed final/title data are prepared at installation; other startup/audio\nand hardware paths still use imported ROM data. The full Pride Lands fidelity\naudit and remaining installation migration are unfinished. This package\ncontains no ROMs or extracted game assets. See the included license files.\n')
    paths = [Path(__file__), build_path, *evidence, ROOT/'scripts/RunInstalledPreview.ps1', ROOT/'Play Installed Preview.cmd']
    report = dict(result='PACKAGED_FOR_VERIFICATION', package=out.relative_to(ROOT).as_posix(),
                  binary_exact=info['player_sha256'] == build['binary_sha256'],
                  existing_settings_modified=False, launcher_source_archived=True, whole_first_level_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'package-report.json').write_text(json.dumps(report, indent=2)+'\n')
    pointer = dict(result='PACKAGED_FOR_VERIFICATION', package_report=(out/'package-report.json').relative_to(ROOT).as_posix(),
                   source_sha256={(out/'package-report.json').relative_to(ROOT).as_posix(): digest(out/'package-report.json')})
    (base/'package-report.json').write_text(json.dumps(pointer, indent=2)+'\n')
    print('PACKAGED', out, info['player_sha256'], flush=True)


if __name__ == '__main__':
    main()
