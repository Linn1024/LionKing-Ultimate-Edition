"""Verify relocated HUD roles survive an actual cross-process player save."""
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
    out = ROOT/'build/pride-hud-rebinding'
    exe = ROOT/'dist/LionKing.exe'
    identity = digest(exe)
    reference = json.loads((out/'report.json').read_text())
    assert reference['candidate_sha256'] == identity
    state = out/'checkpoint.state'
    neutral = out/'neutral.polled.tape'
    neutral.write_bytes(bytes(12000))
    def run(name, source, load=False):
        cmd = [exe, '--rom', ROOT/'Lion King, The (USA).sfc', '--md-rom', ROOT/'Lion King, The (World).md',
               '--resource-profile', out/(source+'.ini'), '--config', out/'host.ini', '--frames', '5400',
               '--input-polled', neutral if load else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
               '--no-pace', '--no-audio', '--no-record', '--dump-window', out/(name+'.png'),
               '--wav', out/(name+'.wav'), '--wav-seconds', '100']
        cmd += ['--load', state] if load else ['--save-at', '5300', state]
        with (out/(name+'.log')).open('wb') as log:
            subprocess.run(list(map(str, cmd)), cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    run('state-save', 'hud')
    assert state.is_file()
    assert pixels(out/'state-save.png') == pixels(out/'candidate.png')
    assert wav_data(out/'state-save.wav') == wav_data(out/'candidate.wav')
    for source, golden in (('hud', 'candidate'), ('native', 'native-5400-new')):
        name = 'state-load-'+source
        run(name, source, True)
        assert hashes(out/(name+'.log')) == hashes(out/(golden+'.log'))
        assert pixels(out/(name+'.png')) == pixels(out/(golden+'.png'))
        pcm = wav_data(out/(name+'.wav'))
        assert pcm and pcm == wav_data(out/(golden+'.wav'))[-len(pcm):]
    assert digest(exe) == identity
    (out/'state-report.json').write_text(json.dumps(dict(result='PASS', scope=__doc__, player_sha256=identity,
        relocated_hud_window_and_complete_pcm_tail_exact=True, cross_graphics_native_fallback_exact=True,
        state_sha256=digest(state), source_sha256=digest(Path(__file__)),
        hud_gate_sha256=digest(out/'report.json'), full_first_level_fidelity_complete=False), indent=2)+'\n')
    print('Post-checkpoint new-process MD/native HUD windows, guest and exact PCM tails PASS', flush=True)


if __name__ == '__main__':
    main()
