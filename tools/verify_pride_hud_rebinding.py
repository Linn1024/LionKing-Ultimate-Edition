"""Compare real Windows HUDs before/after checkpoint task relocation."""
import hashlib
import json
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from verify_windows import hashes, pixels
from verify_pride_audio_state import wav_data


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'build/pride-hud-rebinding'
    report = out / 'report.json'
    report.write_text('{"result":"RUNNING"}\n')
    baseline = out / 'baseline.exe'
    assert digest(baseline) == '95fa2c75bae20aecc605226f505efe9df117f1b8d36c530ed4709a7c9e6be930'
    candidate = ROOT / 'engine/build-win/tlk_sdl.exe'
    identity = digest(candidate)
    (out / 'native.ini').write_text('schema = 1\ngame = snes\n')
    def run(name, exe, profile, frames, mode='lle'):
        cmd = [exe, '--rom', ROOT / 'Lion King, The (USA).sfc', '--md-rom', ROOT / 'Lion King, The (World).md',
               '--resource-profile', out / (profile + '.ini'), '--config', out / 'host.ini',
               '--frames', str(frames), '--input-polled', ROOT / 'build/pride-health-death-native/neutral-tail.polled.tape',
               '--no-pace', '--no-audio', '--no-record', '--dump-window', out / (name + '.png'),
               '--dump-png', out / (name + '-guest.png'), '--wav', out / (name + '.wav'), '--wav-seconds', '100']
        if mode == 'lle':
            cmd.append('--lle')
        with (out / (name + '.log')).open('wb') as log:
            subprocess.run(list(map(str, cmd)), cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    def equal_guest_audio(a, b):
        assert hashes(out / (a + '.log')) == hashes(out / (b + '.log'))
        assert (out / (a + '-guest.png')).read_bytes() == (out / (b + '-guest.png')).read_bytes()
        assert wav_data(out / (a + '.wav')) == wav_data(out / (b + '.wav'))
    # The baseline HUD route was captured before editing/rebuilding the compositor.
    assert (out / 'baseline.png').exists()
    run('candidate', candidate, 'hud', 5400)
    equal_guest_audio('baseline', 'candidate')
    width, height, old = pixels(out / 'baseline.png')
    w, h, new = pixels(out / 'candidate.png')
    assert (w, h) == (width, height) == (512, 448)
    changed = [(i % w, i // w) for i, (a, b) in enumerate(zip(old, new)) if a != b]
    assert changed and all(y < 70 for x, y in changed), 'HUD role correction changed world pixels'
    assert any(x < w // 2 for x, y in changed) and any(x >= w // 2 for x, y in changed)
    run('candidate-aot', candidate, 'hud', 5400, 'aot')
    equal_guest_audio('candidate', 'candidate-aot')
    assert pixels(out / 'candidate.png') == pixels(out / 'candidate-aot.png')
    for profile, end in (('native', 5400), ('hud', 3300)):
        prefix = profile + '-' + str(end)
        run(prefix + '-old', baseline, profile, end)
        run(prefix + '-new', candidate, profile, end)
        equal_guest_audio(prefix + '-old', prefix + '-new')
        assert pixels(out / (prefix + '-old.png')) == pixels(out / (prefix + '-new.png'))
    assert digest(candidate) == identity
    result = dict(result='PASS', scope=__doc__, candidate_sha256=identity, baseline_sha256=digest(baseline),
                  after_reload_changed_pixels=len(changed),
                  after_reload_changed_bbox=[min(x for x,y in changed), min(y for x,y in changed),
                                             max(x for x,y in changed)+1, max(y for x,y in changed)+1],
                  guest_and_complete_pcm_unchanged=True, native_window_unchanged=True,
                  pre_death_md_hud_unchanged=True, aot_lle_window_guest_pcm_exact=True,
                  production_packaged=False, full_first_level_fidelity_complete=False,
                  source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'):digest(p) for p in
                                 (Path(__file__), ROOT/'engine/runner/tlk_hud_role.h',
                                  ROOT/'engine/runner/tlk_wide.c', ROOT/'engine/tests/hud_role_test.c')},
                  artifacts_sha256={p.name:digest(p) for p in sorted(out.iterdir())
                                    if p.suffix in ('.png', '.wav')})
    report.write_text(json.dumps(result, indent=2)+'\n')
    print('Actual Windows relocated HUD corrected; world/guest/full PCM and pre-death/native presentation retained PASS', flush=True)


if __name__ == '__main__':
    main()
