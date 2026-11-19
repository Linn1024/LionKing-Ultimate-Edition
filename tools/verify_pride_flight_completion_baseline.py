"""Compare every full guest field and PCM byte to the preceding complete route."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_flight_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-flight-player'
    previous=ROOT/'build/pride-player/width-completion'
    out=base/'completion-baseline';out.mkdir()
    new_path=base/'width-completion/report.json';old_path=previous/'report.json'
    assert bound(new_path)['result']==bound(old_path)['result']=='PASS'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    paths=[Path(__file__),new_path,old_path,ROOT/'tools/pride_flight_history.py']
    checks={}
    for mode in ('aot','lle'):
        a=base/'width-completion'/mode;b=previous/mode
        rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
        checks[mode+'/all_full_picture_wram_fields']=len(rows(a))==4500 and rows(a)==rows(b)
        checks[mode+'/entire_pcm']=wav_data(a/'route.wav')==wav_data(b/'route.wav')
        checks[mode+'/entire_final_client']=pixels(a/'window.png')==pixels(b/'window.png')
        paths.extend(folder/name for folder in (a,b) for name in ('run.log','route.wav','window.png'))
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,compared_fields=4500,
        previous_complete_route_field_history_preserved=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'complete-route predecessor comparisons',flush=True);assert all(checks.values())


if __name__=='__main__':main()
