"""Build the installer-only sprite exporter and prepare the verified local pair."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out = ROOT/'build/pride-continue-token-assets'; out.mkdir()
    commands = [
        ['cmake', '-S', str(ROOT/'engine/tools/sprite-assets'), '-B', str(out/'tool'), '-G', 'Ninja',
         '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe', '-DCMAKE_MAKE_PROGRAM=C:/mingw32/bin/ninja.exe'],
        ['cmake', '--build', str(out/'tool'), '--target', 'tlk_prepare_sprite_assets', '-j', '4'],
        [str(out/'tool/tlk_prepare_sprite_assets.exe'), '--snes-rom', str(ROOT/'Lion King, The (USA).sfc'),
         '--md-rom', str(ROOT/'Lion King, The (World).md'), '--output', str(out/'sprites.assets')]]
    for label, cmd in zip(('configure', 'build', 'prepare'), commands):
        with (out/(label+'.log')).open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    paths = [Path(__file__), ROOT/'engine/runner/tlk_md_sprites.c', ROOT/'engine/runner/tlk_md_sprites.h',
             ROOT/'engine/runner/tlk_md_sprite_prepare.c', ROOT/'engine/runner/tlk_md_sprite_prepare.h',
             ROOT/'engine/runner/tlk_md_sprite_format.inc', ROOT/'engine/generated/resources/pride_sprite_map.h',
             ROOT/'engine/tools/prepare_sprite_assets.c', ROOT/'engine/cmake/TlkSpriteAssets.cmake',
             ROOT/'engine/tools/sprite-assets/CMakeLists.txt']
    record = (out/'sprites.assets').read_bytes()
    report = dict(result='BUILT', commands=commands, binary_sha256=digest(out/'tool/tlk_prepare_sprite_assets.exe'),
                  package_sha256=digest(out/'sprites.assets'), package_bytes=len(record),
                  mapped_count=int.from_bytes(record[20:24], 'little'), death_count=int.from_bytes(record[156:160], 'little'),
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['package_bytes'], report['mapped_count'], report['death_count'], report['package_sha256'], flush=True)


if __name__ == '__main__': main()
