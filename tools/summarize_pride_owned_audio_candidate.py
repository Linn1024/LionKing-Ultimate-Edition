"""Bind the completed ownership repair gates without closing full Pride scope."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound


def main():
    base=ROOT/'build/pride-bounce-owner-work/player';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==digest(base/'native-engine/tlk_pride_player.exe')==build['binary_sha256']
    destination=base/'ownership-integration-report.json';assert not destination.exists()
    expected={'verification':64,'saves':36,'legacy-source':27,'invalid-saves':20,
        'timed-load2':20,'allbugs-standalone':10,'bounce-music-mix':34,'bounce-pause':8,
        'bounce-restart':12,'audio-device':29,'regression':32,'width-completion':21}
    paths=[Path(__file__),bp,ROOT/'tools/pride_bounce_owner_history.py'];total=0
    for name,count in expected.items():
        p=base/name/'report.json';r=bound(p)
        assert r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values()),p
        paths.append(p);total+=count
    gates=base/'native-gates/play-report.json';r=json.loads(gates.read_text())
    reference=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json'
    assert r['result']=='PASS' and r['route_count']==75 and r['binary_sha256']==build['binary_sha256']
    assert r['routes']==json.loads(reference.read_text())['routes']
    component=ROOT/'build/pride-bounce-owner-work/component/report.json';assert bound(component)['result']=='PASS'
    tests=ROOT/'build/pride-bounce-owner-work/python-tests.log';assert '23 passed, 4 skipped' in tests.read_text()
    remap=ROOT/'build/pride-bounce-owner-work/remap.log';assert 'PASS (0 failed)' in remap.read_text()
    mx=ROOT/'build/pride-bounce-owner-work/exit-mx.log';lines=mx.read_text().splitlines()
    assert sum(x.lower().startswith('unproven') for x in lines)==11
    assert not any(x.lower().startswith('wrong') for x in lines)
    paths.extend((gates,reference,component,tests,remap,mx))
    assert total==313
    report=dict(result='PARTIAL',checks=total,binary_sha256=build['binary_sha256'],
        maintained_native_ownership_repair_verified=True,native75_endpoint_pairs=75,
        native_allbugs_tracked_fields_per_mode=60648,cold_load_combinations=8,
        supported_mixed_completion_verified=True,real_menu_pause_and_restarts_verified=True,
        wasapi_output_verified=True,wasapi_physical_speaker_recording=False,
        static_wrong=0,static_unproven=11,complete_static_proof=False,
        preview_promoted=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL313: maintained ownership gates verified; full Pride scope open',flush=True)


if __name__=='__main__':main()
