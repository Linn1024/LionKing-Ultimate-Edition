"""Integrate prepared HUD loading into the qualified installed-cache player."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound


def main():
    prior = ROOT/'build/pride-installed-cache41'
    old_path = prior/'build-report.json'
    old = bound(old_path)
    out = ROOT/'build/pride-hud-assets42'
    out.mkdir()
    cwd = ROOT/'build/pride-final-standalone'
    frontend = cwd/'native-engine/tlk_pride_final_player_host-frontend/host'
    for patches, source, destination in [('final-frontend-patches', frontend, out/'frontend'),
                                         ('game-patches', ROOT/'engine', out/'game')]:
        subprocess.run(['python', str(ROOT/'engine/scripts/apply_runtime_patches.py'), '--patches',
                        str(ROOT/'engine/cmake'/patches), '--snesrecomp', str(source), '--out', str(destination)],
                       cwd=ROOT, check=True)
    for name in ('tlk_resource_editor_sdl.h', 'tlk_resource_editor_selftest.h'):
        shutil.copyfile(frontend/name, out/'frontend'/name)
    hud_keys = [p for p in old['link_inputs_sha256'] if p.endswith('/tlk_md_hud.c.obj')]
    assert len(hud_keys) == 1
    inputs = argv('link '+(prior/'link.rsp').read_text())[1:]
    compiles = {}
    for label, source, previous in [
        ('host', ROOT/'engine/runner/pride/final/pride_final_host.c', prior/'host.obj'),
        ('resources', out/'game/tlk_resources.c', prior/'resources.obj'),
        ('hud', out/'game/tlk_md_hud.c', ROOT/hud_keys[0]),
        ('hud-assets', ROOT/'engine/runner/tlk_md_hud_assets.c', None)]:
        cmd = old['compiles']['host' if label == 'host' else 'resources'].copy()
        obj = out/(label+'.obj')
        for flag, value in [('-c', source), ('-o', obj), ('-MF', out/(label+'.d')), ('-MT', obj)]:
            cmd[cmd.index(flag)+1] = str(value)
        if label == 'host':
            i = next(i for i, value in enumerate(cmd) if value.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
            cmd[i] = '-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
        if previous:
            indices = [i for i, p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve() == previous]
            assert len(indices) == 1, (label, indices)
            inputs[indices[0]] = obj.as_posix()
        else:
            inputs.append(obj.as_posix())
        compiles[label] = cmd
    rsp = out/'link.rsp'; rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp), '-o', str(out/'player.exe')], cwd=cwd, stdout=log,
                       stderr=subprocess.STDOUT, check=True, timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll', out/'genesis_plus_gx_libretro.dll')
    paths = [Path(__file__), old_path, out/'frontend/sdl_main.c', out/'game/tlk_resources.c',
             out/'game/tlk_md_hud.c', ROOT/'engine/runner/tlk_md_hud_assets.c',
             ROOT/'engine/runner/tlk_md_hud_assets.h', ROOT/'engine/runner/tlk_md_hud_assets_internal.h',
             ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',
             ROOT/'engine/cmake/game-patches/installed-hud-payload.hunks',
             ROOT/'engine/cmake/game-patches/zzzz-installed-hud-resource.hunks',
             ROOT/'engine/cmake/final-frontend-patches/zzzz-installed-hud.hunks']
    linked = {(cwd/p).resolve().relative_to(ROOT).as_posix(): digest(cwd/p)
              for p in inputs if not p.startswith('-')}
    report = dict(result='BUILT', binary_sha256=digest(out/'player.exe'), compiles=compiles,
                  link_inputs_sha256=linked, fresh_standalone_graph_claimed=False,
                  unchanged_prior_inputs=sum(old['link_inputs_sha256'].get(p) == sha for p, sha in linked.items()),
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('BUILT', report['binary_sha256'], 'unchanged', report['unchanged_prior_inputs'], 'total', len(linked), flush=True)


if __name__ == '__main__':
    main()
