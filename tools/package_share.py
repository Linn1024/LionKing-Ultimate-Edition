"""Build a ROM-free Windows download using a small explicit file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--version', default='preview7004')
    parser.add_argument('--archive-name', help='Optional player-facing ZIP filename.')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', args.version):
        parser.error('Use a simple release version without path separators.')
    if args.archive_name and (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,120}\.zip', args.archive_name)):
        parser.error('Use a simple ZIP filename without path separators.')
    out = (args.output or ROOT/'build'/('share-'+args.version)).resolve()
    if not out.is_relative_to((ROOT/'build').resolve()):
        parser.error('Put release staging under ignored build/.')
    out.mkdir(parents=True, exist_ok=False)
    stage = out/'LionKing-Ultimate-Edition'
    stage.mkdir()
    launcher = (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    relative = re.search(r"\$package = Join-Path \$projectRoot '([^']+)'", launcher).group(1)
    package = ROOT/relative
    info = json.loads((package/'package.json').read_text())
    assert digest(package/'LionKing.exe') == info['player_sha256']
    assert digest(package/'genesis_plus_gx_libretro.dll') == info['backend_sha256']
    files = {}

    def copy(source, destination):
        target = stage/destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        files[target.relative_to(stage).as_posix()] = digest(target)

    # Only the player, its own runtime assets and its component notices/source.
    for name in ['LionKing.exe', 'genesis_plus_gx_libretro.dll', 'package.json', 'save-contract.json']:
        copy(package/name, Path(relative)/name)
    for folder in ['assets', 'licenses', 'source']:
        for source in sorted((package/folder).rglob('*')):
            if source.is_file():
                copy(source, Path(relative)/source.relative_to(package))
    # Setup resolves the preparers from dist/, rather than the player folder.
    for name in ['Final', 'Hud', 'Sprite', 'Caption', 'Checkpoint', 'Revival', 'NativeHud', 'Scene']:
        copy(ROOT/f'dist/Prepare{name}Assets.exe', f'dist/Prepare{name}Assets.exe')
    for source in sorted((ROOT/'dist/licenses').glob('*')):
        if source.is_file():
            copy(source, Path('dist/licenses')/source.name)
    for name in ['Setup.ps1', 'RunInstalledPreview.ps1', 'RunBizHawkShader.ps1']:
        copy(ROOT/'scripts'/name, Path('scripts')/name)
    for name in ['native', 'full-genesis', 'snes-visuals-genesis', 'the-best']:
        copy(ROOT/'profiles'/(name+'.ini'), Path('profiles')/(name+'.ini'))
    for name in ['Setup.cmd', 'Play The Best.cmd', 'Play The Best - BizHawk Shader.cmd', 'Play Full Genesis.cmd',
                 'Play SNES Visuals with Genesis Gameplay.cmd']:
        copy(ROOT/name, name)
    # Public default Play uses The best; the developer's existing Play is intact.
    copy(ROOT/'Play The Best.cmd', 'Play.cmd')
    copy(package/'LionKing.exe', 'dist/LionKing.exe')
    copy(ROOT/'docs/SHARING.md', 'README.md')
    copy(ROOT/'CREDITS.md', 'CREDITS.md')
    notice = stage/relative/'LICENSE-NOTES.txt'
    notice.write_text('Unofficial noncommercial development preview. Supply your own SNES USA and Mega Drive World ROMs.\n'
                      'No ROM dumps or extracted game artwork/music are included. The player contains translated game program code.\n'
                      'Runtime components include snesrecomp (PolyForm Noncommercial), recomp-ui/ImGui (MIT), SDL3 (zlib),\n'
                      'and Genesis Plus GX (its included noncommercial license). Preserve all licenses and matching backend source.\n'
                      'Optional BizHawk-style shader sources/notices, including GPL 3xBRZ, are in assets/shaders beside the player.\n'
                      'See README.md and the licenses/ and source/ directories.\n')
    files[notice.relative_to(stage).as_posix()] = digest(notice)
    for path in stage.rglob('*'):
        if not path.is_file():
            continue
        assert path.suffix.lower() not in {'.sfc', '.smc', '.rom', '.state', '.assets', '.rec', '.wav', '.mp4'}, path
        assert not any(part in {'game-data', 'settings', 'generated', '__pycache__'} for part in path.relative_to(stage).parts), path
    # A package manifest lists every shipped file; development package provenance
    # remains separate from the file-integrity manifest for this public ZIP.
    (stage/'FILES.sha256').write_text(''.join(f'{sha}  {name}\n' for name, sha in sorted(files.items())))
    archive = out/(args.archive_name or ('LionKing-Ultimate-Edition-Windows-'+args.version+'.zip'))
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(stage.rglob('*')):
            if path.is_file():
                z.write(path, path.relative_to(out))
    (out/'SHA256SUMS.txt').write_text(f'{digest(archive)}  {archive.name}\n')
    report = dict(result='BUILT_ALLOWLISTED_SHARE_PACKAGE', archive=str(archive),
                  archive_sha256=digest(archive), bytes=archive.stat().st_size,
                  player_sha256=info['player_sha256'], files=files,
                  scope='ROM-free player download, no prepared assets/saves/settings/recordings/generated source; clean installation still requires both ROMs.')
    (out/'report.json').write_text(json.dumps(report, indent=2))
    print(archive)
    print('SHA256 '+report['archive_sha256'])


if __name__ == '__main__':
    main()
