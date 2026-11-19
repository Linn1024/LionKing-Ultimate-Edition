"""Verify the original MD timeout input boundary through real Windows clients."""
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
    base = ROOT/'build/pride-final-timeout'
    out = base/'verification'
    out.mkdir()
    bound(base/'build-report.json')
    old = ROOT/'build/pride-final-scene-compiled-probe/native-control/report.json'
    prototype = bound(old)['commands'][0]
    references = [ROOT/'build/pride-continue-timeout-boundary/report.json',
                  ROOT/'build/pride-continue-timeout-last-edge/report.json']
    for reference in references:
        bound(reference)
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    cases = [('neutral', {}, False), ('directions', {200: 0x100, 400: 0x200}, False),
             ('confirm842', {842: 0x8000}, False), ('confirm843', {843: 0x8000}, False),
             ('confirm844', {844: 0x8000}, False), ('confirm845', {845: 0x8000}, False),
             ('neutral-lle', {}, True), ('disabled', {}, False),
             ('save844', {}, False), ('resume', {}, False)]
    commands = []
    observations = {}
    saved = out/'menu844.state'
    fatal = 3894
    for name, pads, interpreted in cases:
        folder = out/name
        folder.mkdir()
        data = bytearray(Path(prototype[prototype.index('--input')+1]).read_bytes()[:(fatal-1)*2])
        for age in range(1601):
            data += struct.pack('<H', pads.get(age, 0))
        tape = folder/'input.tape'
        tape.write_bytes(data)
        cmd = prototype.copy()
        cmd[0] = str(base/'player.exe')
        cmd[cmd.index('--frames')+1] = str(fatal+(844 if name == 'save844' else 1600))
        cmd[cmd.index('--input')+1] = str(tape)
        if interpreted:
            cmd += ['--lle']
        if name == 'save844':
            cmd += ['--save-at', str(fatal+844), str(saved)]
        elif name == 'resume':
            cmd[cmd.index('--load')+1] = str(saved)
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        env = dict(active)
        if name == 'disabled':
            env['TLK_CONTINUE_TRANSITION'] = '0'
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        observations[name] = json.loads((folder/'scene.json').read_text())['latched_gameplay']
        commands.append(cmd)
        print(name, observations[name], flush=True)
    title = 0x5ab
    checks = {name+'/title': observations[name]['descriptor'] == title
              for name in ('neutral', 'directions', 'confirm845', 'neutral-lle', 'resume')}
    for name in ('confirm842', 'confirm843', 'confirm844'):
        scene = observations[name]
        checks[name+'/continued'] = scene['descriptor'] == 0x387 and scene['health'] == 4 and scene['lives'] == 2
    checks['native_menu_retained_when_disabled'] = observations['disabled']['descriptor'] == 0x57b
    for suffix, compare in [('guest', lambda p: hashes(p/'run.log')),
                            ('actual_window', lambda p: pixels(p/'window.png')),
                            ('full_pcm', lambda p: pcm(p/'audio.wav'))]:
        checks['normal_lle/'+suffix] = compare(out/'neutral') == compare(out/'neutral-lle')
        if suffix != 'full_pcm':
            checks['cold_resume/'+suffix] = compare(out/'neutral') == compare(out/'resume')
    checks['cold_resume/full_pcm'] = pcm(out/'save844/audio.wav')+pcm(out/'resume/audio.wav') == pcm(out/'neutral/audio.wav')
    checks['single_file_save'] = saved.read_bytes()[:8] == b'TLKFSV01'
    checks['saved_before_expiry'] = observations['save844']['descriptor'] == 0x57b
    paths = [Path(__file__), base/'build-report.json', old, *references,
             ROOT/'tools/verify_pride_final_scene_runtime.py']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  observations=observations, commands=commands, public_player_changed=False,
                  complete_title_timing_or_audio_claimed=False, resource_capabilities_changed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
