"""Build and verify a read-only observer on the current private Game Over player."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound
from verify_windows import hashes, pixels
from verify_pride_final_scene_runtime import pcm


def main():
    out = ROOT / 'build/pride-title-upload-native-observer'
    out.mkdir()
    prior = ROOT / 'build/pride-title-upload16'
    build = bound(prior / 'build-report.json')
    old = bound(prior / 'verification/report.json')
    frontend = out / 'frontend'
    shutil.copytree(prior / 'frontend', frontend)
    front = frontend / 'sdl_main.c'
    text = front.read_text()
    anchor = 'FinalSceneCaptureNative(s_pixels);'
    assert text.count(anchor) == 1
    front.write_text(text.replace(anchor, 'TitleSetupCapture(s_pixels); ' + anchor))
    host = ROOT / 'engine/runner/pride/final/pride_final_host.c'
    text = host.read_text()
    text = re.sub(r'#include "([^\"]+)"', lambda m: '#include "' + (host.parent / m[1]).resolve().as_posix() + '"' if (host.parent / m[1]).is_file() else m[0], text)
    source = out / 'host.c'
    observer = ROOT / 'tools/pride_title_audio_observer.inc'
    source.write_text('#include <stdint.h>\nstatic void TitleSetupCapture(const uint8_t *);\n' + text + '\n#include "' + observer.as_posix() + '"\n')
    cmd = build['compiles']['host'].copy()
    obj = out / 'host.obj'
    for flag, value in [('-c', source), ('-o', obj), ('-MF', out / 'host.d'), ('-MT', obj)]:
        cmd[cmd.index(flag) + 1] = str(value)
    i = next(i for i, value in enumerate(cmd) if value.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
    cmd[i] = '-DTLK_PRIDE_FRONTEND_SOURCE="' + (frontend / 'sdl_main.c').as_posix() + '"'
    cwd = ROOT / 'build/pride-final-standalone'
    with (out / 'compile.log').open('wb') as log:
        subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
    inputs = argv('link ' + (prior / 'link.rsp').read_text())[1:]
    inputs[inputs.index((prior / 'host.obj').as_posix())] = obj.as_posix()
    rsp = out / 'link.rsp'
    rsp.write_text(subprocess.list2cmdline(inputs))
    with (out / 'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe', '-O3', '-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@' + str(rsp), '-o', str(out / 'player.exe')], cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    shutil.copyfile(prior / 'genesis_plus_gx_libretro.dll', out / 'genesis_plus_gx_libretro.dll')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env['TLK_FINAL_MD_ART'] = '1'
    checks = {}; commands = {}
    (out / 'host.ini').write_text('opengl = 0\nscale = 2\n')
    for width in (256, 320):
        folder = out / str(width); folder.mkdir()
        cmd = old['commands'][f'{width}-normal700'].copy(); cmd[0] = str(out / 'player.exe')
        for flag, value in [('--config', out / 'host.ini'), ('--dump-window', folder / 'window.png'),
                            ('--dump-scene', folder / 'scene.json'), ('--wav', folder / 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(value)
        with (folder / 'run.log').open('wb') as log:
            result = subprocess.run(cmd, cwd=ROOT, env=dict(env, TLK_TITLE_AUDIO_DIR=str(folder)),
                                    stdout=log, stderr=subprocess.STDOUT, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        reference = prior / f'verification/{width}-normal700'
        checks[f'{width}_exit'] = result.returncode == 0
        checks[f'{width}_guest'] = hashes(folder / 'run.log') == hashes(reference / 'run.log')
        checks[f'{width}_client'] = pixels(folder / 'window.png') == pixels(reference / 'window.png')
        checks[f'{width}_pcm'] = pcm(folder / 'audio.wav') == pcm(reference / 'audio.wav')
        commands[str(width)] = cmd
    paths = [Path(__file__), observer, source, front, prior / 'build-report.json', prior / 'verification/report.json']
    report = dict(result='NEUTRAL' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  observer_only=True, binary_sha256=digest(out / 'player.exe'),
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix(): digest(cwd/p) for p in inputs if not p.startswith('-')},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], sum(checks.values()), '/', len(checks), flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
