"""Relink the reviewed development player with strict explicit scene-cache loads."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound


def main():
    prior = ROOT/'build/pride-porcupine38'
    previous = bound(prior/'build-report.json')
    original = ROOT/'build/pride-porcupine36/build-report.json'
    commands = bound(original)
    out = ROOT/'build/pride-installed-cache41'
    out.mkdir()
    cwd = ROOT/'build/pride-final-standalone'
    base_frontend = cwd/'native-engine/tlk_pride_final_player_host-frontend/host'
    for patches, source, destination in [('final-frontend-patches', base_frontend, out/'frontend'),
                                         ('game-patches', ROOT/'engine', out/'game')]:
        subprocess.run(['python', str(ROOT/'engine/scripts/apply_runtime_patches.py'),
                        '--patches', str(ROOT/'engine/cmake'/patches), '--snesrecomp', str(source),
                        '--out', str(destination)], check=True, cwd=ROOT)
    for name in ('tlk_resource_editor_sdl.h', 'tlk_resource_editor_selftest.h'):
        shutil.copyfile(base_frontend/name, out/'frontend'/name)
    inputs = argv('link '+(prior/'link.rsp').read_text())[1:]
    compiles = {}
    for label, source in [('host', ROOT/'engine/runner/pride/final/pride_final_host.c'),
                          ('resources', out/'game/tlk_resources.c')]:
        cmd = commands['compiles'][label].copy()
        obj = out/(label+'.obj')
        for flag, value in [('-c', source), ('-o', obj), ('-MF', out/(label+'.d')), ('-MT', obj)]:
            cmd[cmd.index(flag)+1] = str(value)
        if label == 'host':
            index = next(i for i, s in enumerate(cmd) if s.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
            cmd[index] = '-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
        old_object = original.parent/(label+'.obj')
        indices = [i for i, p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve() == old_object]
        assert len(indices) == 1, (label, indices)
        inputs[indices[0]] = obj.as_posix()
        compiles[label] = cmd
    rsp = out/'link.rsp'
    rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp), '-o', str(out/'player.exe')], cwd=cwd, stdout=log,
                       stderr=subprocess.STDOUT, check=True, timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll', out/'genesis_plus_gx_libretro.dll')
    paths = [Path(__file__), prior/'build-report.json', original,
             out/'frontend/sdl_main.c', out/'game/tlk_resources.c',
             ROOT/'engine/cmake/game-patches/zz-installed-scene-cache.hunks',
             ROOT/'engine/cmake/final-frontend-patches/zz-installed-scene-cache.hunks']
    current_inputs = {(cwd/p).resolve().relative_to(ROOT).as_posix(): digest(cwd/p)
                      for p in inputs if not p.startswith('-')}
    report = dict(result='BUILT', binary_sha256=digest(out/'player.exe'), compiles=compiles,
                  fresh_standalone_graph_claimed=False, explicit_installed_cache_is_required_when_supplied=True,
                  other_runtime_resource_preparation_migration_complete=False,
                  unchanged_link_inputs=sum(previous['link_inputs_sha256'].get(p) == sha
                                            for p, sha in current_inputs.items()),
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  link_inputs_sha256=current_inputs)
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], 'unchanged inputs', report['unchanged_link_inputs'], flush=True)


if __name__ == '__main__':
    main()
