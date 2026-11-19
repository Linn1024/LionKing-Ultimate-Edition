"""Require the completed mixture to preserve the actual preceding public run."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from pride_scene_template_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-scene-template-work/player';out=base/'completion-baseline';out.mkdir()
    cp=base/'width-completion/report.json';current=bound(cp)
    old=ROOT/'build/pride-bounce-owner-work/player';op=old/'width-completion/report.json';previous=bound(op)
    assert current['result']==previous['result']=='PASS' and all(current['checks'].values()) and all(previous['checks'].values())
    checks={'identical_resource_profile':(base/'launch-completion.ini').read_bytes()==(old/'launch-completion.ini').read_bytes()}
    for mode in ('aot','lle'):
        a=cp.parent/mode;b=op.parent/mode
        rows=lambda folder:re.findall(PATTERN,(folder/'run.log').read_text())
        checks[mode+'/all_4500_preceding_guest_fields']=len(rows(a))==4500 and rows(a)==rows(b)
        checks[mode+'/whole_preceding_pcm']=wav_data(a/'route.wav')==wav_data(b/'route.wav')
        checks[mode+'/whole_preceding_actual_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[mode+'/same_observed_art_coverage']=json.loads((a/'coverage.json').read_text())==json.loads((b/'coverage.json').read_text())
    paths=[Path(__file__),cp,op,base/'launch-completion.ini',old/'launch-completion.ini']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'preceding completion checks; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
