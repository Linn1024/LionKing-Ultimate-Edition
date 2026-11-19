"""Bind prepared native scene bodies to the full, still-open Pride fidelity scope."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_prepared_revival


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_prepared_revival.main()
    path=ROOT/'build/pride-scene-prepare/report.json';report=json.loads(path.read_text())
    assert report['result']=='PREPARED_DECODER_BODY_AND_NATIVE_ABI_VERIFIED_RUNTIME_OPEN'
    assert report['sources']==['native','both'] and report['modes']==['control','prepared','scene','combined']
    assert not report['production_decoder_bypass_enabled']
    assert report['research_host_sha256']==digest(ROOT/'engine/build-win/tlk_scene_prepare_probe.exe')
    for name,sha in report['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for case,run in report['runs'].items():
        folder=path.parent/case
        for key,file in (('tracked_ram_sha256','route.ram'),('events_sha256','decompress.csv'),
                         ('log_sha256','run.log'),('picture_sha256','picture.png')):
            assert run[key]==digest(folder/file),(case,file)
        for file,sha in run['snapshots_sha256'].items():assert sha==digest(folder/file),(case,file)
    for source in ('native','both'):
        runs={mode:report['runs'][source+'-'+mode] for mode in ('control','prepared','scene','combined')}
        assert [runs[mode]['normal_age'] for mode in runs]==[551,487,533,469]
        for mode in ('scene','combined'):
            run=runs[mode];applied=[c for c in run['calls'] if c['prepared_body_applied']]
            assert len(applied)==7 and sum(c['decoded_bytes'] for c in applied)==57756
            assert all(c['death_reload'] and not c['decoder_fields'] for c in applied)
            assert run['normal_restored_map_and_npc_regions_match_original']
    sdl_path=ROOT/'build/pride-scene-prepare-sdl/report.json';sdl=json.loads(sdl_path.read_text())
    assert sdl['result']=='SCENE_PREPARATION_VERIFIED_CROSS_HOST_MIXED_AUDIO_OPEN' and not sdl['production_decoder_bypass_enabled']
    assert sdl['probe_sha256']==digest(ROOT/'engine/build-win/tlk_scene_prepare_sdl.exe')
    assert set(sdl['runs'])=={'native-control','native-combined','both-control','both-combined','both-combined-repeat'}
    for name,sha in sdl['source_sha256'].items():assert sha==digest(ROOT/name),name
    for case,run in sdl['runs'].items():
        combined='combined' in case
        assert run['normal_age']==(469 if combined else 551) and run['prepared_bodies']==(7 if combined else 0)
        assert run['last_second_peak']>0
        for name,sha in run['artifacts_sha256'].items():assert sha==digest(sdl_path.parent/case/name),(case,name)
    assert sdl['runs']['native-combined']['cross_host_full_wram_matches']
    assert not sdl['runs']['both-combined']['cross_host_full_wram_matches']
    assert sdl['runs']['both-combined-repeat']['same_sdl_host_repeat_pcm_guest_and_window_exact']
    parent_path=ROOT/'build/pride-prepared-revival-latest.json';parent=json.loads(parent_path.read_text())
    assert parent['result']=='PARTIAL' and not parent['full_first_level_fidelity_complete']
    result={'result':'PARTIAL','scope':__doc__,'production_sha256':parent['production_sha256'],
        'original_decoder_abi_cases':8,'actual_windows_pcm_cases':5,'prepared_native_scene_payload_bytes':57756,'prepared_decoder_bodies':7,
        'cross_host_full_mixed_wram_equivalence_verified':False,
        'normal_play_age_original':551,'normal_play_age_bank_only':487,'normal_play_age_scene_only':533,
        'normal_play_age_combined':469,'production_decoder_bypass_enabled':False,
        'full_first_level_fidelity_complete':False,
        'source_sha256':{'script':digest(Path(__file__)),'scene_report':digest(path),'sdl_report':digest(sdl_path),'retained_gates':digest(parent_path)},
        'remaining':['Resolve or separately model headless/SDL mixed-audio publishing; full cross-host RAM equality is unproven',
                     'Coordinate native entry/exit and waits with the verified MD scene clock',
                     'Prepare remaining VRAM/actor work and bank/audio transitions before replacement visibility',
                     'Integrate owned rendering and source palettes without violating per-scene layer evidence',
                     'Implement player lifetime/outer saves, then verify actual Windows/source switching/interruptions']+parent['remaining']}
    (ROOT/'build/pride-scene-prepare-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Prepared scene bodies: eight LLE/five Windows cases; mixed cross-host RAM gap retained, full Pride integration PARTIAL',flush=True)


if __name__=='__main__':main()
