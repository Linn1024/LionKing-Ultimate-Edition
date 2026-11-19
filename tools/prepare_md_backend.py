"""Apply the owned audio-continuation patch and package matching backend source."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT/'.tools/genesis-plus-gx'
PATCH = ROOT/'engine/patches/genesis-plus-gx/0001-audio-continuation.patch'
REVISION = 'a5834b3df455c49bb97bfaa328c20845831f576b'
STAMP = CORE/'tlk-build.json'
SOURCE = ROOT/'dist/source/Genesis-Plus-GX-source.zip'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('apply', 'package', 'check'))
    action = parser.parse_args().action
    if action == 'check':
        try:
            revision = subprocess.run(['git', '-C', str(CORE), 'rev-parse', 'HEAD'], capture_output=True, text=True)
            assert revision.returncode == 0 and revision.stdout.strip() == REVISION
            row = json.loads(STAMP.read_text())
            assert row['patch_sha256'] == digest(PATCH)
            assert row['dll_sha256'] == digest(CORE/'genesis_plus_gx_libretro.dll')
            assert row['source_sha256'] == digest(SOURCE)
        except (OSError, ValueError, KeyError, AssertionError):
            raise SystemExit(1)
        return
    assert subprocess.check_output(['git', '-C', str(CORE), 'rev-parse', 'HEAD'], text=True).strip() == REVISION
    if action == 'apply':
        command = ['git', '-C', str(CORE), 'apply']
        already = subprocess.run(command+['--reverse', '--check', str(PATCH)], capture_output=True)
        if already.returncode:
            subprocess.run(command+['--check', str(PATCH)], check=True)
            subprocess.run(command+[str(PATCH)], check=True)
        print('MD audio continuation patch ready', flush=True)
        return
    # Include complete tracked source, including the core's vendored components,
    # with our modifications. Object files, ROMs and local captures are excluded.
    names = subprocess.check_output(['git', '-C', str(CORE), 'ls-files', '--recurse-submodules', '-z']).decode().split('\0')
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SOURCE, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            if name and (CORE/name).is_file():
                archive.write(CORE/name, 'Genesis-Plus-GX/'+name)
        archive.write(PATCH, 'tlk-patches/'+PATCH.name)
        archive.writestr('TLK-SOURCE.txt', 'Genesis Plus GX '+REVISION+'\n'
                        'TLK audio continuation extension revision 1.\n'
                        'Build: mingw32-make -f Makefile.libretro platform=win HAVE_CHD=0 '
                        'HAVE_SYS_PARAM=0 HOOK_CPU=1 CPPFLAGS=-fcommon '
                        "'SHARED=-shared -static-libgcc -Wl,--export-all-symbols' -j8\n")
    STAMP.write_text(json.dumps({'revision': REVISION, 'audio_state_revision': 1,
                                'patch_sha256': digest(PATCH),
                                'dll_sha256': digest(CORE/'genesis_plus_gx_libretro.dll'),
                                'source_sha256': digest(SOURCE)}, indent=2)+'\n')
    print('Matching MD backend source packaged:', SOURCE, flush=True)


if __name__ == '__main__':
    main()
