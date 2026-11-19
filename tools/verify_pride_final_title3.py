"""Verify direct native title return, pending-exit saves and usable Start."""
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
    base = ROOT/'build/pride-final-title3'
    out = base/'verification'
    out.mkdir()
    bound(base/'build-report.json')
    reference = ROOT/'build/pride-final-timeout/verification/report.json'
    template = bound(reference)['commands'][0]
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    active = dict(clean, TLK_FINAL_SKIP='0', TLK_FINAL_LATE_SKIP='1', TLK_FINAL_FAST_ASSETS='1',
                  TLK_FINAL_SCENE_PRESENT='1', TLK_CONTINUE_FAST_RELOAD='1',
                  TLK_CONTINUE_BANK_APPLY='1', TLK_CONTINUE_TRANSITION='1')
    cases = [('old330', 'no', 330, None), ('no330', 'no', 330, None),
             ('no1000', 'no', 1000, None), ('timeout1600', 'timeout', 1600, None),
             ('save180', 'no', 180, None), ('resume180', 'no', 1000, 'save180'),
             ('save240', 'no', 240, None), ('resume240', 'no', 1000, 'save240'),
             ('save360', 'no', 360, None), ('resume360', 'no', 1000, 'save360'),
             ('save885', 'timeout', 885, None), ('resume885', 'timeout', 1600, 'save885'),
             ('start', 'start', 1600, None)]
    commands = []
    observations = {}
    fatal = 3894
    for name, protocol, end, restored in cases:
        folder = out/name
        folder.mkdir()
        data = bytearray(Path(template[template.index('--input')+1]).read_bytes()[:(fatal-1)*2])
        for age in range(1601):
            pad = 0
            if protocol in ('no', 'start'):
                if 130 <= age <= 133:
                    pad = 0x100
                elif 140 <= age <= 143:
                    pad = 0x8000
                elif protocol == 'start' and 500 <= age <= 503:
                    pad = 0x1000
            data += struct.pack('<H', pad)
        tape = folder/'input.tape'
        tape.write_bytes(data)
        cmd = template.copy()
        cmd[0] = str(ROOT/'build/pride-final-timeout/player.exe') if name == 'old330' else str(base/'player.exe')
        cmd[cmd.index('--frames')+1] = str(fatal+end)
        cmd[cmd.index('--input')+1] = str(tape)
        if name.startswith('save'):
            cmd += ['--save-at', str(fatal+end), str(folder/'saved.state')]
        if restored:
            cmd[cmd.index('--load')+1] = str(out/restored/'saved.state')
        for flag, filename in [('--dump-window', 'window.png'), ('--dump-scene', 'scene.json'), ('--wav', 'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(folder/filename)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd, cwd=ROOT, env=active, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        observations[name] = json.loads((folder/'scene.json').read_text())['latched_gameplay']
        commands.append(cmd)
        print(name, observations[name], flush=True)
    checks = dict(old330_still_intro=observations['old330']['descriptor'] == 0x57b,
                  no330_actual_title=observations['no330']['descriptor'] == 0x5ab,
                  no330_visible=sum(pixel != (0, 0, 0) for pixel in pixels(out/'no330/window.png')[2]) > 10000,
                  no1000_title=observations['no1000']['descriptor'] == 0x5ab,
                  timeout1600_title=observations['timeout1600']['descriptor'] == 0x5ab,
                  start_plays_pride=observations['start']['descriptor'] == 0x387 and observations['start']['health'] == 4)
    for name, resumed, direct, pending in [('save180', 'resume180', 'no1000', True),
                                           ('save240', 'resume240', 'no1000', True),
                                           ('save360', 'resume360', 'no1000', False),
                                           ('save885', 'resume885', 'timeout1600', True)]:
        data = (out/name/'saved.state').read_bytes()
        native = struct.unpack_from('<I', data, 20)[0]
        flags = struct.unpack_from('<I', data, 96+native+108)[0]
        checks[name+'/pending_intent'] = bool(flags & 128) == pending
        checks[name+'/guest'] = hashes(out/resumed/'run.log') == hashes(out/direct/'run.log')
        checks[name+'/actual_client'] = pixels(out/resumed/'window.png') == pixels(out/direct/'window.png')
        checks[name+'/full_pcm'] = pcm(out/name/'audio.wav')+pcm(out/resumed/'audio.wav') == pcm(out/direct/'audio.wav')
    paths = [Path(__file__), base/'build-report.json', reference]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  observations=observations, commands=commands, public_player_changed=False,
                  exact_md_exit_timing_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p)
                                    for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
