"""Build the maintained direct-title return against the audited standalone player."""
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
    baseline = build/'build-report.json'
    bound(baseline)
    out = ROOT/'build/pride-final-title3'
    out.mkdir()
    generation = ROOT/'build/pride-final-title-hooks2/generation-report.json'
    generated = bound(generation)
    public = ROOT/'build/pride-arena-work/tlk_pride_player.exe'
    before = digest(public)
    db = json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe', '-t', 'compdb'], cwd=build))
    host = next(row for row in db if row.get('file', '').endswith('/final/pride_final_host.c'))
    state = next(row for row in db if row.get('file', '').endswith('/tlk_final_scene_state.c') and '/tlk_pride_final_player.dir/' in row['output'])
    tasks = [('host', host, Path(host['file'])), ('state', state, ROOT/'engine/runner/tlk_final_scene_state.c')]
    changed = []
    for name in generated['instrumented_units']:
        entry = next(row for row in db if row.get('file', '').endswith('/'+name)
                     and any(part in row['output'] for part in ('/tlk_pride_final_player_guest.dir/', '/tlk_pride_final_player_native.dir/')))
        source = generation.parent/'hooks'/name
        if digest(source) != digest(Path(entry['file'])):
            tasks.append((name, entry, source))
            changed.append(name)
    assert changed == ['bankc0_part01_v2.c', 'bankc4_part1c_v2.c'], changed
    replacements = {}
    for name, entry, source in tasks:
        obj = out/(name+'.obj')
        cmd = argv(entry['command'])
        cmd += ['-I'+str(ROOT/'engine/runner/pride')]
        for flag, value in [('-c', source), ('-o', obj), ('-MF', out/(name+'.d')), ('-MT', obj)]:
            cmd[cmd.index(flag)+1] = str(value)
        with (out/(name+'-compile.log')).open('wb') as log:
            subprocess.run(cmd, cwd=build, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
        replacements[entry['output']] = obj.as_posix()
    lines = (build/'build.ninja').read_text().splitlines()
    start = next(i for i, row in enumerate(lines) if row.startswith('build native-engine/tlk_pride_final_player.exe:'))
    inputs = lines[start].split(': ', 1)[1].split(' ', 1)[1].split(' |')[0].split()
    for old, new in replacements.items():
        assert inputs.count(old) == 1
        inputs[inputs.index(old)] = new
    libraries = next(row.split(' = ', 1)[1] for row in lines[start+1:] if row.startswith('  LINK_LIBRARIES ='))
    inputs += argv('link '+libraries)[1:]
    rsp = out/'link.rsp'
    rsp.write_text(subprocess.list2cmdline(inputs))
    binary = out/'player.exe'
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp), '-o', str(binary)], cwd=build, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=180)
    shutil.copyfile(build/'genesis_plus_gx_libretro.dll', out/'genesis_plus_gx_libretro.dll')
    assert digest(public) == before
    paths = [Path(__file__), baseline, generation, ROOT/'engine/runner/tlk_continue_menu.h', ROOT/'engine/runner/tlk_final_scene_state.h',
             ROOT/'engine/recomp/pride_final_hooks.json',
             *sorted((ROOT/'engine/runner/pride/final').glob('*.inc')),
             *[source for _, _, source in tasks]]
    report = dict(result='BUILT', binary_sha256=digest(binary), changed_guest_units=changed,
                  public_player_unchanged=True, fresh_standalone_graph_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  link_inputs_sha256={(build/p).resolve().relative_to(ROOT).as_posix(): digest(build/p)
                                      for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], flush=True)


if __name__ == '__main__':
    main()
