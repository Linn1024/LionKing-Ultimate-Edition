"""Build owned NO/timeout fade and skip the native pre-fade wait."""
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
    build = ROOT/'build/pride-final-standalone'
    prior = ROOT/'build/pride-title-lifecycle'
    bound(prior/'build-report.json')
    generation = ROOT/'build/pride-title-fade-hooks/generation-report.json'
    generated = bound(generation)
    previous_generation = ROOT/'build/pride-final-title-hooks2'
    changed = [name for name in generated['instrumented_units']
               if digest(generation.parent/'hooks'/name) != digest(previous_generation/'hooks'/name)]
    assert changed == ['bankc0_part01_v2.c'], changed
    out = ROOT/'build/pride-title-fade'
    out.mkdir()
    db = json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe', '-t', 'compdb'], cwd=build))
    host = next(row for row in db if row.get('file', '').endswith('/final/pride_final_host.c'))
    state = next(row for row in db if row.get('file', '').endswith('/tlk_final_scene_state.c') and '/tlk_pride_final_player.dir/' in row['output'])
    guest = next(row for row in db if row.get('file', '').endswith('/bankc0_part01_v2.c') and '/tlk_pride_final_player_guest.dir/' in row['output'])
    old_guest = ROOT/'build/pride-final-title3'
    tasks = [('host', host, Path(host['file']), prior/'host.obj'),
             ('state', state, ROOT/'engine/runner/tlk_final_scene_state.c', old_guest/'state.obj'),
             ('guest', guest, generation.parent/'hooks/bankc0_part01_v2.c', old_guest/'bankc0_part01_v2.c.obj')]
    inputs = argv('link '+(prior/'link.rsp').read_text())[1:]
    for name, entry, source, previous in tasks:
        cmd = argv(entry['command'])
        obj = out/(name+'.obj')
        for flag, value in [('-c', source), ('-o', obj), ('-MF', out/(name+'.d')), ('-MT', obj)]:
            cmd[cmd.index(flag)+1] = str(value)
        with (out/(name+'-compile.log')).open('wb') as log:
            subprocess.run(cmd, cwd=build, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
        assert inputs.count(previous.as_posix()) == 1
        inputs[inputs.index(previous.as_posix())] = obj.as_posix()
    rsp = out/'link.rsp'
    rsp.write_text(subprocess.list2cmdline(inputs))
    binary = out/'player.exe'
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp), '-o', str(binary)], cwd=build, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll', out/'genesis_plus_gx_libretro.dll')
    paths = [Path(__file__), prior/'build-report.json', generation,
             ROOT/'engine/runner/tlk_final_scene_state.h', ROOT/'engine/recomp/pride_final_hooks.json',
             *[source for _, _, source, _ in tasks], *sorted((ROOT/'engine/runner/pride/final').glob('*.inc'))]
    report = dict(result='BUILT', binary_sha256=digest(binary), changed_guest_units=changed,
                  fresh_standalone_graph_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  link_inputs_sha256={(build/p).resolve().relative_to(ROOT).as_posix(): digest(build/p)
                                      for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], flush=True)


if __name__ == '__main__':
    main()
