"""Bind native reload ownership/prepared-bank evidence with the full open Pride scope."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_revival_scene


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_revival_scene.main()
    folder=ROOT/'build/pride-native-reload-owner';path=folder/'report.json';report=json.loads(path.read_text())
    assert report['result']=='NATIVE_RELOAD_OWNERSHIP_AND_BANK_BYTES_VERIFIED_RUNTIME_OPEN'
    assert report['sources']==['native','both'] and report['experiments']==['fast','drain','batch','cached']
    assert report['execution_mode']=='LLE only' and len(report['runs'])==10
    assert report['original_controls_unchanged'] and not report['production_death_gameplay_enabled']
    assert report['player_sha256']==digest(ROOT/'dist/LionKing.exe')
    assert report['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe')
    assert report['research_host_sha256']==digest(ROOT/'engine/build-win/tlk_pride_reload_probe.exe')
    assert digest(ROOT/'Lion King, The (USA).sfc')=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert digest(ROOT/'Lion King, The (World).md')=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    for name,sha in report['source_sha256'].items():assert sha==digest(ROOT/name),name
    for name,run in report['runs'].items():
        for key,file in [('events_sha256','events.csv'),('field_samples_sha256','fields.csv'),('complete_tracked_ram_sha256','route.ram'),
                         ('run_log_sha256','run.log'),('picture_sha256','picture.png')]:
            assert run[key]==digest(folder/name/file),(name,key)
        for file,sha in run.get('snapshots_sha256',{}).items():assert sha==digest(folder/name/file),(name,file)
        for file,sha in run.get('template_files_sha256',{}).items():assert sha==digest(folder/name/file),(name,file)
    for source in ('native','both'):
        control=report['runs'][source+'-control'];fast=report['runs'][source+'-fast']
        batch=report['runs'][source+'-batch'];cached=report['runs'][source+'-cached'];drain=report['runs'][source+'-drain']
        assert control['sample_bank_host_fields']==batch['sample_bank_host_fields']==64
        assert control['points']['c32b24']['relative_field']==551
        assert fast['comparison']['original_sample_blocks_matched']==list(range(14,20))
        assert not fast['comparison']['sample_arena_matches_at_return']
        assert drain['outcome']=='BANK_NOT_READY_WITHIN_5400_FIELDS'
        assert batch['comparison']['original_sample_blocks_matched']==list(range(20))
        assert batch['comparison']['sample_arena_matches_at_return'] and not batch['comparison']['normal_entry_fields_saved']
        assert cached['sample_bank_host_fields']==0 and cached['points']['c32b24']['relative_field']==487
        comparison=cached['comparison']
        assert comparison['original_sample_blocks_matched']==list(range(20)) and comparison['original_score_exact_at_return']
        assert comparison['sample_arena_matches_at_return'] and comparison['sample_arena_matches_at_normal_play']
        assert comparison['original_sample_bytes']==43560 and comparison['original_score_bytes']==6250
        assert comparison['unchanged_before_sample_bank'] and comparison['same_restored_level_map_and_graphics']
        metadata=json.loads((folder/(source+'-cached')/'template-metadata.json').read_text())
        assert metadata['dsp_gain']==[0]*8 and metadata['port_queue']==metadata['driver_flags']==0
        assert metadata['field']<cached['points']['c089b7']['host_field']
    parent_path=ROOT/'build/pride-revival-scene-latest.json';parent=json.loads(parent_path.read_text())
    assert parent['result']=='PARTIAL' and not parent['full_first_level_fidelity_complete']
    assert report['runs']['native-cached']['guest']==report['runs']['both-cached']['guest']
    result={'result':'PARTIAL','scope':__doc__,'player_sha256':report['player_sha256'],'headless_sha256':report['headless_sha256'],
        'read_only_native_reload_controls':2,'research_cases':10,'prepared_bank_source_music_combinations':2,
        'prepared_original_score_bytes':6250,'prepared_original_sample_bytes':43560,'prepared_sample_blocks':20,
        'native_bank_fields_original':64,'native_bank_fields_prepared':0,'prototype_normal_play_age':487,
        'unrestricted_fast_flag_rejected':True,'unwritten_reserved_directory_entries_preserved':True,
        'production_controller_enabled':False,'full_first_level_fidelity_complete':False,
        'source_sha256':{'script':digest(Path(__file__)),'reload_probe':digest(path),'retained_gates':digest(parent_path)},
        'remaining':['Move prepared native bank ownership into a guarded reusable player component',
                     'Verify native PCM, audio-ring/clock ownership and serialized template continuation',
                     'Prepare remaining scene data and actor state before MD reload deadlines',
                     'Integrate original CPU entry/return, renderer, audio and outer saves; verify actual Windows and interruptions']+parent['remaining']}
    (ROOT/'build/pride-native-reload-owner-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Prepared native bank prototype and reload ownership verified in LLE; player integration/full Pride fidelity remain PARTIAL',flush=True)


if __name__=='__main__':main()
