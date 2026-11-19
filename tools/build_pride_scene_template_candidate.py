"""Build the fallback-decoder repair through the maintained standalone graph."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-scene-template-work';base.mkdir()
    out=base/'player'
    configure=['C:/mingw32/bin/cmake.exe','-S',str(ROOT/'engine/player'),'-B',str(out),'-G','Ninja',
        '-C',str(ROOT/'engine/player/windows32.cmake'),'-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_MAKE_PROGRAM=C:/mingw32/bin/ninja.exe','-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe',
        '-DCMAKE_CXX_COMPILER=C:/mingw32/bin/g++.exe','-DTLK_PRIDE_ROM='+str(ROOT/'Lion King, The (USA).sfc'),
        '-DTLK_PRIDE_GENERATION='+str(ROOT/'build/pride-bounce-owner-work/game-program')]
    build=['C:/mingw32/bin/cmake.exe','--build',str(out),'--target','tlk_pride_player','-j','8']
    for name,command in (('configure',configure),('build',build)):
        with (base/(name+'.log')).open('wb') as log:
            subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=2400)
        print(name,'complete',flush=True)
    exe=out/'native-engine/tlk_pride_player.exe'
    report=dict(result='BUILT',binary_sha256=digest(exe),configure=configure,build=build,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),ROOT/'engine/runner/pride/pride_scene_template.h',ROOT/'build/pride-scene-template-baseline/report.json']})
    (base/'commands.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Fresh fallback candidate',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
