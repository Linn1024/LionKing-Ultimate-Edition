"""Publish verified phase boundaries without enabling an incomplete behavior source."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    retained_path=ROOT/'build/pride-death-art-latest.json'
    retained=json.loads(retained_path.read_text());assert retained['result']=='PARTIAL'
    assert retained['player_sha256']==digest(ROOT/'dist/LionKing.exe')
    assert retained['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe')
    native_path=ROOT/'build/pride-death-phases/comparison.json'
    native=json.loads(native_path.read_text())
    assert native['result']=='SOUND_SOURCE_INDEPENDENT_NATIVE_PHASES_MD_PRESENTATION_OPEN'
    assert native['headless_sha256']==retained['headless_sha256']
    assert native['all_music_sources_full_wram_identical']
    assert native['per_source_aot_lle_full_wram_equal_fields']==1001
    md_path=ROOT/'build/pride-death-presentation-md/comparison.json'
    md=json.loads(md_path.read_text());assert md['result']=='PASS'
    mappings={'analysis':ROOT/'tools/compare_pride_death_phases.py',
              'capture':ROOT/'build/pride-death-phases/report.json',
              'reload_capture':ROOT/'build/pride-death-reload/report.json',
              'md_presentation':ROOT/'build/pride-death-presentation-md/report.json'}
    for name,path in mappings.items():assert native['source_sha256'][name]==digest(path),name
    mappings={'analysis':ROOT/'tools/compare_md_death_presentation.py',
              'capture':ROOT/'build/pride-death-presentation-md/report.json',
              'timeline':ROOT/'build/pride-death-timeline/report.json'}
    for name,path in mappings.items():assert md['source_sha256'][name]==digest(path),name
    ordinary=json.loads((ROOT/'build/pride-death-timeline/report.json').read_text())
    native_case=native['native_music_source_phase_signatures']['native'];start=native_case['health_zero_field']
    native_relative={k:v-start for k,v in native_case.items() if k.endswith('_field')}
    md_start=ordinary['md_deaths'][0]['death']
    md_relative={'selective_fade_start':0,'main_loop_start':24,'main_loop_end':225,
                 'complete_fade_end':249,'positive_health':270,
                 'new_hero_owner':md['new_global_hero_owner_field']-md_start,
                 'first_returning_cub_palette_color':md['first_returning_cub_palette_color_field']-md_start,
                 'cub_palette_fully_restored':md['cub_palette_fully_restored_field']-md_start}
    result={'result':'PARTIAL','scope':__doc__,'player_sha256':retained['player_sha256'],
            'headless_sha256':retained['headless_sha256'],'production_binary_changed':False,
            'native_power_on_runs':16,'native_music_choices':4,'full_wram_equal_fields_per_choice':1001,
            'native_music_source_phase_independence_verified':True,'md_captured_video_fields':409,
            'native_relative_snapshot_fields':native_relative,'md_relative_video_fields':md_relative,
            'md_fade_interval_fields':3,'md_palette_dma_latency_fields':1,
            'md_selective_fade_preserves_palette0':True,'md_post_display_fade_affects_all_palettes':True,
            'production_death_gameplay_source_enabled':False,'full_first_level_fidelity_complete':False,
            'source_sha256':{'script':digest(Path(__file__)),'native_comparison':digest(native_path),
                             'md_comparison':digest(md_path),'retained_artwork_and_regressions':digest(retained_path)},
            'remaining':['Implement a video-field-owned death phase clock and presentation with supported mixed sources',
                         'Prepare native graphics/checkpoint data without inheriting the native reload stall',
                         'Preserve independent audio, final-life skip, source profiles and pause/save/continue boundaries']+retained['remaining']}
    (ROOT/'build/pride-death-phases-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Death/reload phase evidence verified; selectable gameplay implementation remains open',flush=True)


if __name__=='__main__':main()
