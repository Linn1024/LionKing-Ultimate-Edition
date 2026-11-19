"""Fresh standalone CMake build of maintained native audio ownership."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-bounce-owner-work';out=base/'player'
    assert not out.exists()
    configure=['C:/mingw32/bin/cmake.exe','-S',str(ROOT/'engine/player'),'-B',str(out),'-G','Ninja',
        '-C',str(ROOT/'engine/player/windows32.cmake'),'-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_MAKE_PROGRAM=C:/mingw32/bin/ninja.exe','-DCMAKE_C_COMPILER=C:/mingw32/bin/gcc.exe',
        '-DCMAKE_CXX_COMPILER=C:/mingw32/bin/g++.exe',
        '-DTLK_PRIDE_ROM='+str(ROOT/'Lion King, The (USA).sfc'),
        '-DTLK_PRIDE_GENERATION='+str(base/'game-program')]
    build=['C:/mingw32/bin/cmake.exe','--build',str(out),'--target','tlk_pride_player','-j','8']
    for label,command in (('configure',configure),('build',build)):
        with (base/(label+'.log')).open('wb') as log:
            subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=2400)
        print(label,'completed',flush=True)
    exe=out/'native-engine/tlk_pride_player.exe'
    (base/'commands.json').write_text(json.dumps(dict(configure=configure,build=build,
        source_sha256={Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__))},binary_sha256=digest(exe)),indent=2)+'\n')
    print('Fresh maintained ownership player built',digest(exe),flush=True)


if __name__=='__main__':main()
