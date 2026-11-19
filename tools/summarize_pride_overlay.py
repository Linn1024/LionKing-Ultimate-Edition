"""Strict source/link/artifact aggregate for mixed notification composition."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import read_rows, toast_image
from verify_pride_overlay import mixed_toast
from verify_windows import hashes, pixels


def main():
    base=ROOT/'build/pride-overlay'; build_path=base/'build-report.json'; build=bound(build_path)
    for name,sha in build['production_sha256'].items(): assert digest(ROOT/name)==sha,name
    for host,r in build['runs'].items():
        assert digest(base/f'overlay-{host}.exe')==r['binary_sha256']
        for name,sha in r['link_inputs_sha256'].items(): assert digest(ROOT/name)==sha,name
    paths=[Path(__file__),build_path,ROOT/'tools/summarize_pride_practice.py']; reports={}; checks={}; count=0; total_pixels=0
    for case in ('md-owned','native-owned','md-ordinary','native-ordinary','md-owned-software'):
        path=base/'windows'/case/'report.json'; r=bound(path); paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values()),case
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
        reports[case]=digest(path); count+=len(r['checks']); total_pixels+=r['pixels_compared']
        folder=path.parent
        checks[case+'-oracle']=pixels(folder/'candidate/window.png')==mixed_toast(folder/'control/window.png','Slot 1: Ordinary-play save is incompatible or damaged')
    # With no overlay, the candidate must preserve the preceding source-bound
    # real windows and the complete frozen rendering/audio/guest evidence.
    for name,previous in (('md','crc-md'),('native','backend-native')):
        old=ROOT/'build/pride-practice/verified/rejection'/previous
        report=bound(old/'report.json'); paths.append(old/'report.json')
        assert report['result']=='PASS' and all(report['checks'].values())
        new=base/'windows'/(name+'-owned')
        checks[name+'-previous-control-window']=pixels(new/'control/window.png')==pixels(old/'control/window.png')
        checks[name+'-previous-control-guest']=hashes(new/'control/run.log')==hashes(old/'control/run.log')
        checks[name+'-previous-control-pcm']=wav_data(new/'control/audio.wav')==wav_data(old/'control/audio.wav')
        for file in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv','bank-clock.csv'):
            checks[name+'-previous-'+file]=read_rows(new/'control'/file)==read_rows(old/'control'/file)
        for file in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv'):
            checks[name+'-previous-'+file]=digest(new/'control/restart-1'/file)==digest(old/'control/restart-1'/file)
        if name=='md':
            legacy=toast_image(new/'control/window.png',new/'control/guest.png','Slot 1: Ordinary-play save is incompatible or damaged')
            checks['reproduced-old-native-imprint']=legacy==pixels(old/'candidate/window.png')
            checks['corrected-md-notification']=pixels(new/'candidate/window.png')!=legacy
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    result=dict(result='PARTIAL',scope=__doc__,reports_sha256=reports,checks=checks,
        checks_passed=count+len(checks),complete_client_pixels=total_pixels,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        mixed_notification_blending_verified=True,guest_and_native_pcm_preserved=True,
        public_player_enabled=False,mixed_ui_overlay_fidelity_complete=False,
        full_first_level_fidelity_complete=False,
        remaining='Practice/turbo/menu overlays, UI-free save materialization, F9 from owned revival, source/audio/reset/legacy and full first-level/public integration.')
    (ROOT/'build/pride-overlay-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL mixed notifications:',len(reports),'reports;',result['checks_passed'],'checks;',total_pixels,'client pixels',flush=True)


if __name__=='__main__':main()
