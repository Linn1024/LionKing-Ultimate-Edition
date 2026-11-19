"""Bind reusable native-bank evidence without closing the full Pride checklist."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_reload_owner


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_reload_owner.main()
    folder=ROOT/'build/pride-native-bank'
    path=folder/'report.json';record_path=folder/'records/report.json'
    report=json.loads(path.read_text());records=json.loads(record_path.read_text())
    assert report['result']==records['result']=='PASS'
    assert report['sources']==['native','both']
    assert report['original_controls_unchanged'] and report['new_process_prepared_bank_continuation']
    assert not report['production_component_enabled'] and report['production_binaries_unchanged']
    for result in (report,records):
        for name,sha in result['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert report['probe_sha256']==digest(ROOT/'engine/build-win/tlk_native_bank_probe.exe')
    assert records['test_sha256']==digest(ROOT/'engine/build-win/tlk_native_bank_test.exe')
    for key,file in (('player_sha256','dist/LionKing.exe'),('headless_sha256','engine/build-win/tlk_headless.exe')):
        assert report[key]==digest(ROOT/file)
    for source,runs in report['runs'].items():
        assert set(runs)=={'control','prepared','loaded'}
        for mode,run in runs.items():
            case=folder/(source+'-'+mode)
            assert run['normal_age']==(551 if mode=='control' else 487)
            assert run['bank_fields']==(64 if mode=='control' else 0)
            for key,file in (('events_sha256','events.csv'),('tracked_ram_sha256','route.ram'),
                             ('log_sha256','run.log'),('picture_sha256','picture.png')):
                assert run[key]==digest(case/file),(source,mode,file)
            for file,sha in run['files_sha256'].items():assert digest(case/file)==sha,(source,mode,file)
    for file,sha in records['artifacts_sha256'].items():assert digest(folder/'records'/file)==sha,file
    assert records['record_bytes']==99639 and records['source_buffer_detachment']
    assert records['source_build_and_semantic_record_guards'] and records['failed_load_and_apply_preserve_live_state']
    assert records['live_dsp_echo_ring_and_clocks_preserved']
    assert records['queued_pcm_frames_preserved']==37 and records['new_pcm_frames']==6250
    assert records['new_process_continuation_spc_cycles']==200000
    parent_path=ROOT/'build/pride-native-reload-owner-latest.json';parent=json.loads(parent_path.read_text())
    assert parent['result']=='PARTIAL' and not parent['full_first_level_fidelity_complete']
    result={'result':'PARTIAL','scope':__doc__,
        'player_sha256':report['player_sha256'],'headless_sha256':report['headless_sha256'],
        'reusable_component_vm_cases':6,'new_process_record_bytes':99639,
        'queued_pcm_frames_preserved':37,'new_pcm_frames':6250,'continued_spc_cycles':200000,
        'bank_fields_original':64,'bank_fields_prepared':0,'normal_play_age_prepared':487,
        'production_component_enabled':False,'full_first_level_fidelity_complete':False,
        'source_sha256':{'script':digest(Path(__file__)),'vm_report':digest(path),
                         'record_report':digest(record_path),'retained_gates':digest(parent_path)},
        'remaining':['Integrate bank lifetime, audio-thread locking and outer-game saves in the player',
                     'Verify actual native song/output continuity through the bank swap',
                     'Prepare remaining scene data and actor state before MD reload deadlines',
                     'Integrate CPU, scene clock, renderer and audio; verify real Windows/F12/pause interruptions']
                    +parent['remaining'][2:]}
    (ROOT/'build/pride-native-bank-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Reusable native-bank VM/record/PCM-preservation gates PASS; player integration/full Pride fidelity remain PARTIAL',flush=True)


if __name__=='__main__':main()
