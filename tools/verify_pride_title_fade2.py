"""Verify real Windows frozen-menu fade phases and cold-process resumes."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes, pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base = ROOT/'build/pride-title-fade2'
    out = base/'verification'
    out.mkdir()
    bound(base/'build-report.json')
    reference = ROOT/'build/pride-final-title3/verification/report.json'
    original = bound(reference)
    no = original['commands'][2]
    timeout = original['commands'][3]
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    commands = []
    scenes = {}
    checks = {}
    def run(name, protocol, age, save=False, restored=None, old=False, interpreted=False):
        folder = out/name
        folder.mkdir()
        cmd = (no if protocol == 'no' else timeout).copy()
        cmd[0] = str(ROOT/'build/pride-title-lifecycle/player.exe') if old else str(base/'player.exe')
        cmd[cmd.index('--frames')+1] = str(3894+age)
        if save:
            cmd += ['--save-at', str(3894+age), str(folder/'saved.state')]
        if restored:
            cmd[cmd.index('--load')+1] = str(out/restored/'saved.state')
        if interpreted:
            cmd += ['--lle']
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=active, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
        scenes[name] = json.loads((folder/'scene.json').read_text())['latched_gameplay']
        print(name, 'completed', flush=True)
    run('old140', 'no', 140, old=True)
    for age in (140,141,143,144,146,147,149,150,152,153,155,156,158,159,160,278,279):
        run('no'+str(age), 'no', age, save=age == 150)
    for age in (844,845,847,848,850,862,863,864,983,984):
        run('timeout'+str(age), 'timeout', age, save=age == 844)
    run('resume160', 'no', 160, restored='no150')
    run('resume845', 'timeout', 845, restored='timeout844')
    run('interpreted159', 'no', 159, interpreted=True)
    def expected(image, elapsed):
        step = min(7, (elapsed+2)//3)
        loss = (step*31+3)//7
        def component(c):
            value = max(0, (c >> 3)-loss)
            return (value << 3) | (value >> 2)
        return image[:2], [tuple(component(c) for c in p) for p in image[2]]
    checks['no140_original_native_canvas'] = pixels(out/'no140/window.png') == pixels(out/'old140/window.png')
    for protocol, origin, ages in [('no',140,(141,143,144,146,147,149,150,152,153,155,156,158,159,160)),
                                   ('timeout',844,(845,847,848,850,862,863,864))]:
        source = pixels(out/f'{protocol}{origin}/window.png')
        for age in ages:
            image = pixels(out/f'{protocol}{age}/window.png')
            shape, colors = expected(source, age-origin)
            checks[f'{protocol}{age}/entire_frozen_canvas'] = image[:2] == shape and image[2] == colors
    for saved, resumed, direct in [('no150','resume160','no160'), ('timeout844','resume845','timeout845')]:
        checks[saved+'/cold_guest'] = hashes(out/resumed/'run.log') == hashes(out/direct/'run.log')
        checks[saved+'/cold_client'] = pixels(out/resumed/'window.png') == pixels(out/direct/'window.png')
        checks[saved+'/cold_pcm'] = pcm(out/saved/'audio.wav')+pcm(out/resumed/'audio.wav') == pcm(out/direct/'audio.wav')
    for suffix, getter in [('guest',lambda p:hashes(p/'run.log')), ('client',lambda p:pixels(p/'window.png')),
                           ('pcm',lambda p:pcm(p/'audio.wav'))]:
        checks['normal_lle/'+suffix] = getter(out/'no159') == getter(out/'interpreted159')
    for name in ('no278','timeout983'):
        checks[name+'/still_black'] = not any(p != (0,0,0) for p in pixels(out/name/'window.png')[2])
    for name in ('no279','timeout984'):
        checks[name+'/title_reached'] = scenes[name]['descriptor'] == 0x5ab and any(p != (0,0,0) for p in pixels(out/name/'window.png')[2])
    paths = [Path(__file__), base/'build-report.json', reference, ROOT/'build/pride-title-exit-fade-reference/report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, scenes=scenes,
                  commands=commands, public_player_changed=False, full_md_title_timing_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
