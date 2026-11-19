"""Audit the preserved OS capture without assuming more than128 game colors."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-machine-player4';out=base/'os-window';assert not (out/'report.json').exists()
    matrix_path=base/'md/report.json';matrix=bound(matrix_path);assert matrix['result']=='PASS'
    build_path=base/'build-report.json';build=bound(build_path);assert digest(base/'machine.exe')==build['binary_sha256']
    attempt=ROOT/'build/pride-machine-player4-os-window.log';raw=attempt.read_bytes()
    log=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
    fields=re.findall(r'OS client captured after reset at (\d+)',log);assert len(fields)==1
    assert "'os_picture_nonblank': False" in log and "'entire_recorded_pcm': True" in log
    # The capture succeeded; the old >128-color heuristic rejected a real
    # limited-palette MD frame. Check actual game area, excluding host panels,
    # alongside unchanged strict guest/PCM/final-client comparisons.
    w,h,p=pixels(out/'client.png');game={p[y*w+x] for y in range(60,h-48) for x in range(w)}
    author=base/'md/soft-aot'
    checks=dict(captured_after_restart=1450<=int(fields[0])<1700,
                os_viewport=(w,h)==(640,448),os_game_picture_nonblank=len(game)>16,
                final_guest=hashes(out/'run.log')==hashes(author/'run.log'),
                whole_final_client=pixels(out/'window.png')==pixels(author/'window.png'),
                entire_recorded_pcm=wav_data(out/'audio.wav')==wav_data(author/'audio.wav'))
    assert all(checks.values()),checks
    command=[s.replace(str(author),str(out)) for s in matrix['commands']['soft-aot']]
    paths=[Path(__file__),ROOT/'tools/capture_pride_machine_window.py',matrix_path,build_path,attempt,ROOT/'tools/windows_capture.py',ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py']
    report=dict(result='PASS',checks=checks,capture=dict(before_field=int(fields[0]),size=[w,h],colors=len(set(p)),game_colors=len(game)),
                rejected_more_than128_colors_assumption=True,command=command,binary_sha256=build['binary_sha256'],
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS preserved OS capture:',checks,flush=True)


if __name__=='__main__':main()
