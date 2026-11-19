"""Record actual 320-wide final-life clients without claiming width support.

The prefatal backend is an ordinary native checkpoint. Changing presentation
width here isolates the renderer; it is not evidence for a power-on 320 route.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels, hashes


def main():
    out = ROOT / 'build/pride-final-wide-probe2'
    out.mkdir()
    build = ROOT / 'build/pride-final-arena-phase/build-report.json'
    bound(build)
    fixture = ROOT / 'build/pride-final-arena-fixture/report.json'
    source = bound(fixture)
    exe = ROOT / 'build/pride-final-arena-phase/player.exe'
    profile = out / 'resources.ini'
    profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'
                       'gameplay.levels.pride_lands.health_death = md\n'
                       'graphics.scenery = md\n')
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1',
                  TLK_FINAL_FAST_ASSETS='1', TLK_FINAL_SCENE_PRESENT='1',
                  TLK_CONTINUE_FAST_RELOAD='1', TLK_CONTINUE_BANK_APPLY='1',
                  TLK_CONTINUE_TRANSITION='1')
    runs = {}
    for name, age, enabled, save in [('control0', 0, False, False),
                                      ('control1', 1, False, False),
                                      ('final0', 0, True, False),
                                      ('final7', 7, True, False),
                                      ('black19', 19, True, False),
                                      ('save7', 7, True, True)]:
        folder = out / name
        folder.mkdir()
        cmd = source['commands']['control0'].copy()
        cmd[0] = str(exe)
        for flag, value in [('--resource-profile', profile),
                            ('--frames', source['fatal_field'] + age),
                            ('--dump-window', folder / 'window.png'),
                            ('--dump-scene', folder / 'scene.json')]:
            cmd[cmd.index(flag) + 1] = str(value)
        if save:
            cmd += ['--save-at', str(source['fatal_field'] + age), str(folder / 'saved.state')]
        with (folder / 'run.log').open('wb') as log:
            result = subprocess.run(cmd, cwd=ROOT, env=active if enabled else clean,
                                    stdout=log, stderr=subprocess.STDOUT, timeout=120)
        info = dict(command=cmd, returncode=result.returncode,
                    save_exists=(folder / 'saved.state').exists())
        if (folder / 'window.png').exists():
            width, height, rgb = pixels(folder / 'window.png')
            # The actual Windows client is scaled uniformly from 320x224.
            assert width * 224 == height * 320, (width, height)
            margin = width * 32 // 320
            centre = [p for i, p in enumerate(rgb) if margin <= i % width < width - margin]
            sides = [p for i, p in enumerate(rgb) if not margin <= i % width < width - margin]
            info.update(client_size=[width, height], centre_lit=sum(any(p) for p in centre),
                        side_lit=sum(any(p) for p in sides), guest=hashes(folder / 'run.log'))
        runs[name] = info
    def faded(image, age):
        loss = (((age + 2) // 3) * 31 + 3) // 7
        def component(c):
            value = max(0, (c >> 3) - loss)
            return value << 3 | value >> 2
        return image[0], image[1], [tuple(component(c) for c in p) for p in image[2]]
    checks = dict(
        captures_succeeded=all(runs[n]['returncode'] == 0 for n in ('control0', 'final0', 'final7', 'black19')),
        centre_is_black19=runs['black19']['centre_lit'] == 0,
        sides_also_black19=runs['black19']['side_lit'] == 0,
        selected_origin_lost=pixels(out/'control0/window.png') != pixels(out/'final0/window.png'),
        selected_whole_fade_wrong=pixels(out/'final7/window.png') != faded(pixels(out/'control1/window.png'), 7),
        width320_save_not_created=not runs['save7']['save_exists'],
    )
    report = dict(result='REPRODUCED' if all(checks.values()) else 'UNEXPECTED',
                  checks=checks, runs=runs, binary_sha256=digest(exe),
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p)
                                 for p in (Path(__file__), build, fixture)},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                   for p in out.rglob('*') if p.is_file()})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
