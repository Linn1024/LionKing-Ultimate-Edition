"""Build read-only scene/decoder observations against the private timeout player."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound


def main():
    prior = ROOT/'build/pride-final-title3'
    bound(prior/'build-report.json')
    build = ROOT/'build/pride-final-standalone'
    out = ROOT/'build/pride-final-title-observer3'
    out.mkdir()
    frontend = out/'frontend'
    shutil.copytree(build/'native-engine/tlk_pride_final_player_host-frontend/final', frontend)
    path = frontend/'sdl_main.c'
    text = path.read_text()
    old = 'FinalSceneCaptureNative(s_pixels);'
    assert text.count(old) == 1
    path.write_text(text.replace(old, old+' TitleCapture(s_pixels);'))
    source = out/'host.c'
    host = ROOT/'engine/runner/pride/final/pride_final_host.c'
    text = host.read_text()
    text = text.replace('#include "../tlk_pride_host.c"', '#include "'+(host.parent.parent/'tlk_pride_host.c').as_posix()+'"')
    text = text.replace('#include "pride_final_assets.inc"', '#include "'+(host.parent/'pride_final_assets.inc').as_posix()+'"')
    text = text.replace('#include "pride_final_runtime.inc"', '#include "'+(host.parent/'pride_final_runtime.inc').as_posix()+'"')
    source.write_text('#include <stdint.h>\nstatic void TitleCapture(const uint8_t *);\n'+text+
                      '\n#include "'+(ROOT/'tools/pride_final_title_observer.inc').as_posix()+'"\n')
    db = json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe', '-t', 'compdb'], cwd=build))
    entry = next(row for row in db if row.get('file', '').endswith('/final/pride_final_host.c'))
    cmd = argv(entry['command'])
    obj = out/'host.obj'
    for flag, value in [('-c', source), ('-o', obj), ('-MF', out/'host.d'), ('-MT', obj)]:
        cmd[cmd.index(flag)+1] = str(value)
    i = next(i for i, value in enumerate(cmd) if value.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
    cmd[i] = '-DTLK_PRIDE_FRONTEND_SOURCE="'+(frontend/'sdl_main.c').as_posix()+'"'
    with (out/'compile.log').open('wb') as log:
        subprocess.run(cmd, cwd=build, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
    inputs = argv('link '+(prior/'link.rsp').read_text())[1:]
    previous = (prior/'host.obj').as_posix()
    assert inputs.count(previous) == 1
    inputs[inputs.index(previous)] = obj.as_posix()
    rsp = out/'link.rsp'
    rsp.write_text(subprocess.list2cmdline(inputs))
    binary = out/'player.exe'
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp), '-o', str(binary)], cwd=build, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll', out/'genesis_plus_gx_libretro.dll')
    paths = [Path(__file__), prior/'build-report.json', source, path, ROOT/'tools/pride_final_title_observer.inc']
    report = dict(result='BUILT', binary_sha256=digest(binary), observer_only=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], flush=True)


if __name__ == '__main__':
    main()
