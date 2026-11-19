"""Bind the partial cold-restart audit, including its unresolved audio difference."""
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_audio_state import wav_data

BASE=ROOT/'build/pride-restart'


def bound(path,artifacts=True):
    r=json.loads(path.read_text())
    for name,sha in r['source_sha256'].items():assert digest(ROOT/name)==sha,(path,name)
    if artifacts:
        for name,sha in r.get('artifacts_sha256',{}).items():assert digest(path.parent/name)==sha,(path,name)
    return r


def main():
    build_path=BASE/'build-report.json';build=bound(build_path)
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for host,r in build['runs'].items():
        assert digest(BASE/f'restart-{host}.exe')==r['binary_sha256']
        for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    reproduction_path=ROOT/'build/pride-restart-reproduction/report.json';reproduction=bound(reproduction_path)
    assert reproduction['exit']==0 and not reproduction['boot_state_exists']
    path=BASE/'final/windows/native-aot/report.json';native=bound(path)
    assert native['result']=='INCOMPLETE'
    assert [n for n,v in native['checks'].items() if not v]==['before/pcm']
    assert all(v==0 for v in native['exits'].values())
    assert native['binary_sha256']==build['runs']['sdl']['binary_sha256']
    save_paths=[BASE/f'final/owned-saves/{n}/report.json' for n in (0,1)]
    for save_path in save_paths:
        r=bound(save_path);assert r['result']=='PASS' and all(r['checks'].values())
        assert r['binary_sha256']==build['runs']['probe']['binary_sha256']
    diagnostic_path=BASE/'audio-diagnostic/report.json';diagnostic=bound(diagnostic_path)
    states=[]
    for case in diagnostic['cases']:
        field=case['field'];assert field in (2761,2762) and case['pcm_tail_equal'] and not case['state_equal']
        a=(BASE/f'audio-diagnostic/{field}-baseline/owned.state').read_bytes()
        b=(BASE/f'audio-diagnostic/{field}-before/owned.state').read_bytes();assert len(a)==len(b)
        at=a.index(b'TLKAUD01');assert b.index(b'TLKAUD01')==at
        phase=at+128+32784
        allowed=((56,88),(at+80,at+112),(phase,phase+16))
        differences=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
        assert differences and all(any(lo<=i<hi for lo,hi in allowed) for i in differences)
        states.append(dict(field=field,baseline_phase_occupancy=struct.unpack_from('<2d',a,phase),
            restored_phase_occupancy=struct.unpack_from('<2d',b,phase),other_state_bytes_exact=True))
    consumer_path=BASE/'consumer-trace/report.json';consumer=bound(consumer_path)
    assert consumer['differences']==301 and consumer['first'][0]==dict(field='2700',changes=dict(write=['1438001','1438002']))
    folder=BASE/'final/windows/native-aot';pcm=wav_data(folder/'baseline/audio.wav');live=wav_data(folder/'before/audio.wav')
    prefix=len(live)-len(pcm);assert prefix>0 and live[:prefix]==pcm[:prefix]
    first=next(i for i,(a,b) in enumerate(zip(pcm,live[prefix:])) if a!=b);assert first==8825444
    sources=[Path(__file__),build_path,reproduction_path,path,*save_paths,diagnostic_path,consumer_path,
             ROOT/'tools/verify_pride_audio_state.py']
    report=dict(result='INCOMPLETE',scope=__doc__,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        native_checks_passed=sum(native['checks'].values()),native_checks_total=len(native['checks']),
        owned_cross_mode_saves=2,consumer_first_difference_field=2700,consumer_transient_extra_native_samples=1,
        first_replayed_pcm_difference_byte=first,state_comparisons=states,
        pristine_save_and_new_process_restore_verified=True,native_scripted_live_restore_guest_pixels_verified=True,
        native_before_death_restore_pcm_verified=False,md_restart_verified=False,actual_live_level_menu_verified=False,
        practice_f9_restart_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-restart-latest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Cold restart INCOMPLETE:',report['native_checks_passed'],'/',report['native_checks_total'],
          'native checks; first consumer difference2700, PCM byte',first,flush=True)


if __name__=='__main__':main()
