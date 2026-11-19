"""Check checkpoint graphics choices after a real cross-process player save."""
import hashlib
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from verify_windows import hashes, pixels
from verify_pride_audio_state import wav_data


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parent = ROOT/'build/pride-checkpoint-player/windows-5400'
    reference_path = parent/'report.json'
    reference = json.loads(reference_path.read_text())
    assert reference['result'] == 'PASS'
    exe = ROOT/'engine/build-win/tlk_sdl.exe'
    identity = digest(exe)
    assert identity == reference['candidate_sha256']
    for file, sha in reference['source_sha256'].items():
        assert digest(ROOT/file) == sha, file
    out = ROOT/'build/pride-checkpoint-player/state'
    out.mkdir(exist_ok=True)
    neutral = out/'neutral.polled.tape'
    neutral.write_bytes(bytes(24000))
    cases = {}
    for width in (256, 320):
        state = parent/f'{width}-both-aot/checkpoint.state'
        assert state.is_file()
        for source in ('native','frames','palette','both'):
            for mode in ('aot','lle'):
                key = f'{width}-{source}-{mode}'
                folder = out/key
                folder.mkdir(exist_ok=True)
                golden = parent/key
                cmd = [exe, '--rom', ROOT/'Lion King, The (USA).sfc', '--md-rom', ROOT/'Lion King, The (World).md',
                       '--resource-profile', golden/'resources.ini', '--config', parent/'host.ini',
                       '--load', state, '--frames', '5400', '--input-polled', neutral,
                       '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
                       '--wav',folder/'audio.wav','--wav-seconds','100']
                if mode == 'lle':
                    cmd.append('--lle')
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
                assert hashes(folder/'run.log') == hashes(golden/'run.log')
                assert pixels(folder/'window.png') == pixels(golden/'window.png')
                pcm = wav_data(folder/'audio.wav')
                assert pcm and pcm == wav_data(golden/'audio.wav')[-len(pcm):]
                cases[key] = dict(state_sha256=digest(state),cross_source_window_and_guest_exact=True,
                    complete_pcm_tail_exact=True,artifacts_sha256={p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()})
                print(key,'new-process source choice/window/guest/PCM tail PASS',flush=True)
    old_state = ROOT/'build/pride-hud-rebinding/checkpoint.state'
    old_report_path = ROOT/'build/pride-hud-rebinding/state-report.json'
    old_report = json.loads(old_report_path.read_text())
    assert old_report['result'] == 'PASS' and old_report['state_sha256'] == digest(old_state)
    folder = out/'previous-shipped-save'
    folder.mkdir(exist_ok=True)
    golden = parent/'256-both-aot'
    cmd = [exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
           '--resource-profile',golden/'resources.ini','--config',parent/'host.ini','--load',old_state,
           '--frames','5400','--input-polled',neutral,'--no-pace','--no-audio','--no-record',
           '--dump-window',folder/'window.png','--wav',folder/'audio.wav','--wav-seconds','100']
    with (folder/'run.log').open('wb') as log:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    assert hashes(folder/'run.log') == hashes(golden/'run.log')
    assert pixels(folder/'window.png') == pixels(golden/'window.png')
    pcm = wav_data(folder/'audio.wav')
    assert pcm and pcm == wav_data(golden/'audio.wav')[-len(pcm):]
    cases['previous-shipped-save'] = dict(state_sha256=digest(old_state),cross_source_window_and_guest_exact=True,
        complete_pcm_tail_exact=True,artifacts_sha256={p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()})
    assert digest(exe) == identity
    report = dict(result='PASS',scope=__doc__,candidate_sha256=identity,cases=cases,
        reference_sha256=digest(reference_path),source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        previous_shipped_save_exact=True, previous_save_report_sha256=digest(old_report_path),
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
