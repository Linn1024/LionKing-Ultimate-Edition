"""Stage maintained sources in a separate repository; never stage the workspace wholesale."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/github-share6996'
EXTENSIONS = {'.c', '.cpp', '.h', '.hpp', '.py', '.ps1', '.sh', '.cmake', '.cfg',
              '.toml', '.rs', '.lock', '.hunks', '.patch', '.rc', '.inc'}
DIRS = {'runner', 'recomp', 'cmake', 'patches', 'scripts', 'tools', 'player', 'player-final'}


def main():
    OUT.mkdir(exist_ok=False)
    copied = {}

    def copy(source, relative):
        target = OUT/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied[str(relative).replace('\\', '/')] = hashlib.sha256(target.read_bytes()).hexdigest()

    # Git's existing exclusions suppress generated/ and all build trees. Limit
    # the snapshot to maintained source directories; frameworks stay upstream.
    raw = subprocess.check_output(['git', '-C', str(ROOT/'engine'), 'ls-files',
                                   '--cached', '--others', '--exclude-standard', '-z'])
    for name in sorted(set(x.decode() for x in raw.split(b'\0') if x)):
        rel = Path(name)
        source = ROOT/'engine'/rel
        if not source.is_file() or source.is_symlink():
            continue
        if rel.parts[0] in DIRS and (source.suffix in EXTENSIONS or source.name == 'CMakeLists.txt'):
            copy(source, Path('engine')/rel)
    for name in ['CMakeLists.txt', 'LICENSE', 'AGENTS.md']:
        copy(ROOT/'engine'/name, Path('engine')/name)
    for source in sorted((ROOT/'engine/packaging').glob('LICENSE-*.txt')):
        copy(source, Path('engine/packaging')/source.name)
    # Build/decode tools are source; bounded one-off research scripts are not
    # release inputs. No ROM-derived output files are copied.
    for source in sorted((ROOT/'tools').glob('*.py')):
        if 'fidelity' not in source.name and not source.name.startswith('record_'):
            copy(source, Path('tools')/source.name)
    copy(ROOT/'tools/record_video.py', 'tools/record_video.py')
    for source in sorted((ROOT/'profiles').glob('*.ini')):
        copy(source, Path('profiles')/source.name)
    for name in ['Build.ps1', 'BuildMDResearch.ps1', 'Setup.ps1', 'RunInstalledPreview.ps1']:
        copy(ROOT/'scripts'/name, Path('scripts')/name)
    for name in ['Setup.cmd', 'Play The Best.cmd', 'Play Full Genesis.cmd',
                 'Play SNES Visuals with Genesis Gameplay.cmd', 'Record Video.cmd']:
        copy(ROOT/name, name)
    copy(ROOT/'Play The Best.cmd', 'Play.cmd')
    copy(ROOT/'docs/SHARING.md', 'README.md')
    copy(ROOT/'docs/VIDEO-SCRIPT.md', 'VIDEO-SCRIPT.md')
    copy(ROOT/'docs/background-audit.md', 'docs/background-audit.md')
    copy(ROOT/'AGENTS.md', 'AGENTS.md')
    for name in ['HOW_IT_WORKS.md', 'VERIFYING.md']:
        copy(ROOT/'engine/docs'/name, Path('engine/docs')/name)
    copy(ROOT/'engine/tools/README.md', 'engine/tools/README.md')
    (OUT/'docs/HANDOFF.md').write_text('# Shared preview source handoff\n\n'
        'Start with ../SOURCE-NOTES.md and ../README.md. Preview6996 is a development build.\n'
        'The source snapshot has not been certified to reproduce the incremental release binary.\n'
        'Do not commit ROMs, extracted assets, generated game code or recordings.\n'
        'Keep both frameworks unmodified at the revisions in ../dependencies.json.\n'
        'Background changes require per-scene evidence; see background-audit.md.\n')
    deps = {}
    for name, url in [('snesrecomp', 'https://github.com/RetroPortingToolKit/snesrecomp.git'),
                      ('recomp-ui', 'https://github.com/RetroPortingToolKit/recomp-ui.git')]:
        revision = subprocess.check_output(['git', '-C', str(ROOT/'engine'/name), 'rev-parse', 'HEAD'], text=True).strip()
        deps[name] = dict(url=url, revision=revision)
    (OUT/'dependencies.json').write_text(json.dumps(deps, indent=2))
    (OUT/'.gitignore').write_text('build/\ndist/\nsettings/\ngame-data/\n.tools/\n'
                                'engine/snesrecomp/\nengine/recomp-ui/\nengine/generated/\n'
                                'engine/build*/\n__pycache__/\n*.pyc\n*.sfc\n*.smc\n*.rom\n*.bin\n'
                                '*.assets\n*.state\n*.rec\n*.mp4\n*.wav\n*.log\n*.exe\n*.dll\n*.zip\n')
    (OUT/'SOURCE-NOTES.md').write_text('''# Source snapshot and credits

This is the maintained project source snapshot accompanying preview6996.
The working Windows binary has been built incrementally from reviewed local
objects. A byte-for-byte clean rebuild from this snapshot is not yet certified;
use the Windows ZIP in Releases to play. Some development tools reference local
ignored research history; those tools are not required by the installer.

Based on [TLKRecomp by kinduff and contributors](https://github.com/kinduff/TLKRecomp).
Port source license: engine/LICENSE. Framework URLs/revisions: dependencies.json.
Fetch those frameworks into engine/snesrecomp and engine/recomp-ui before trying
scripts/Build.ps1. Frameworks must be kept unmodified. The generator takes your
local original ROM and produces ignored engine/generated files.

No ROM, extracted game assets, generated game source, saves, recordings or
personal settings are committed. The binary includes translated program code;
it and the matching backend source/licenses are distributed as release assets.

The Lion King is an original Disney/Virgin Interactive game. This is an unofficial
fan project. The combined runtime is noncommercial; see the packaged licenses.
''')
    (OUT/'source-manifest.json').write_text(json.dumps(dict(files=copied,
        upstream_tlkrecomp_revision=subprocess.check_output(['git', '-C', str(ROOT/'engine'), 'rev-parse', 'HEAD'], text=True).strip(),
        player_sha256='a1986f7f9f029ae6aec8b6ed4a591467d9f4d5a6820c9166dd9d8694c969aa53'), indent=2))
    paths = list(OUT.rglob('*'))
    assert not any(p.suffix.lower() in {'.sfc', '.smc', '.rom', '.bin', '.assets', '.state', '.rec', '.wav', '.mp4', '.exe', '.dll'} for p in paths if p.is_file())
    print('SOURCE_SNAPSHOT', len(copied), 'files,', sum(p.stat().st_size for p in paths if p.is_file()), 'bytes')


if __name__ == '__main__':
    main()
