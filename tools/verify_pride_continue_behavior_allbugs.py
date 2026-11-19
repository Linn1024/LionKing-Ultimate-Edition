"""Verify observer neutrality and all native All Bugs tracked fields on candidate41."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    base = ROOT/'build/pride-continue-token-behavior50'
    observer = base/'allbugs-observer'
    build_path = observer/'build-report.json'
    build = bound(build_path)
    assert digest(observer/'player.exe') == build['binary_sha256']
    assert all(digest(ROOT/p) == sha for p, sha in build['link_inputs_sha256'].items())
    out = base/'allbugs-verification'
    out.mkdir()
    source = ROOT/'build/pride-sprite-fresh44/runtime-verification/report.json'
    verified = bound(source)
    template = verified['commands']['full-aot'].copy()
    template[template.index('--sprite-assets')+1]=str(ROOT/'build/pride-continue-token-assets/sprites.assets')
    i = template.index('--hash-at'); del template[i:i+2]
    reference = ROOT/'build/pride-reset/fixed4/native/gates'
    tape = ROOT/'engine/tapes/allbugsF.read.tape'
    template[template.index('--input-polled')+1] = str(tape)
    clean = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    clean['SDL_VIDEODRIVER'] = 'dummy'
    checks = {}
    commands = {}
    def run(label, frames, mode='aot', observe=False):
        folder = out/label
        folder.mkdir()
        cmd = template.copy()
        cmd[0] = str(observer/'player.exe' if observe else base/'player.exe')
        cmd[cmd.index('--frames')+1] = str(frames)
        for flag in ('--dump-window', '--dump-scene', '--wav', '--wav-seconds'):
            i = cmd.index(flag); del cmd[i:i+2]
        config = folder/'host.ini'; config.write_text('opengl = 0\nscale = 1\n')
        profile = folder/'resources.ini'; profile.write_text('schema = 1\ngame = snes\n')
        for flag, value in [('--config', config), ('--resource-profile', profile)]:
            cmd[cmd.index(flag)+1] = str(value)
        if frames == 3000:
            cmd += ['--hash-at', ','.join(map(str, range(1, 3001))), '--wav', str(folder/'audio.wav'), '--wav-seconds', '60']
        if mode == 'lle': cmd += ['--lle']
        env = clean.copy()
        if observe: env['TLK_TRACKED_RAM_LOG'] = str(folder/'route.ram')
        commands[label] = cmd
        with (folder/'run.log').open('wb') as log:
            rc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=1800, creationflags=subprocess.CREATE_NO_WINDOW).returncode
        text = (folder/'run.log').read_text()
        print(label, rc, hashes(folder/'run.log'), flush=True)
        return folder, rc, text
    normal, rc, text = run('pilot-control', 3000)
    checks['pilot_control_exit_and_cache'] = rc == 0 and 'resource_cache=loaded' in text
    pilot, rc, text = run('pilot-observer', 3000, observe=True)
    checks['pilot_observer_exit_and_cache'] = rc == 0 and 'resource_cache=loaded' in text
    rows = lambda folder: re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)', (folder/'run.log').read_text())
    checks['pilot_all3000_picture_and_wram_fields_neutral'] = len(rows(normal)) == 3000 and rows(normal) == rows(pilot)
    checks['pilot_endpoint_neutral'] = hashes(normal/'run.log') == hashes(pilot/'run.log')
    checks['pilot_whole_pcm_neutral'] = digest(normal/'audio.wav') == digest(pilot/'audio.wav')
    checks['pilot_original_tracked_fields'] = (pilot/'route.ram').read_bytes().splitlines() == (reference/'allbugs-aot.ram').read_bytes().splitlines()[:3000]
    endpoints = {}
    if all(checks.values()):
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {mode: pool.submit(run, mode, 60648, mode, True) for mode in ('aot', 'lle')}
            endpoints = {mode: future.result() for mode, future in futures.items()}
        for mode, (folder, rc, text) in endpoints.items():
            actual = (folder/'route.ram').read_bytes().splitlines()
            expected = (reference/('allbugs-'+mode+'.ram')).read_bytes().splitlines()
            checks[mode+'_exit_and_cache'] = rc == 0 and 'resource_cache=loaded' in text
            checks[mode+'_all60648_tracked_fields'] = len(actual) == 60648 and actual == expected
            checks[mode+'_original_endpoint'] = hashes(folder/'run.log') == dict(
                frame_sha256='0326bd99ae26d38d67e782f83f4fbf2a3d2ec956a78d4cf7533f93668cab1cb5',
                wram_sha256='a0930247992cac1ea728412f4386001df57154c2635ece64e7e8717f02e26f9e')
        checks['allbugs_modes_every_tracked_field'] = (out/'aot/route.ram').read_bytes() == (out/'lle/route.ram').read_bytes()
    paths = [Path(__file__), build_path, base/'build-report.json', source, tape,
             reference/'allbugs-aot.ram', reference/'allbugs-lle.ram']
    report = dict(result='PASS' if all(checks.values()) and endpoints else 'FAIL', checks=checks,
                  commands=commands, allbugs_fields_per_mode=60648, observer_only=True,
                  production_allbugs_every_field_directly_logged=False, new_external_emulator_capture=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
