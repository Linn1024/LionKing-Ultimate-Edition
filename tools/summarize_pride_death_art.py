"""Bind current death artwork/timeline evidence and retained Pride gates."""
import hashlib
import json
from audit_scenes import ROOT
import summarize_pride_game_over


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_game_over.main()
    player=ROOT/'dist/LionKing.exe';headless=ROOT/'engine/build-win/tlk_headless.exe'
    ph,hh=digest(player),digest(headless)
    reports={}
    def read(name,result='PASS'):
        path=ROOT/'build'/name;value=json.loads(path.read_text())
        assert value['result']==result,(name,value['result'])
        assert path.stat().st_mtime_ns>=max(player.stat().st_mtime_ns,headless.stat().st_mtime_ns),name
        if 'player_sha256' in value:assert value['player_sha256']==ph,name
        if 'headless_sha256' in value:assert value['headless_sha256']==hh,name
        reports[name]=digest(path)
        return value
    art=read('pride-death-art/report.json')
    assert art['unique_death_frames']==20 and art['ordinary_power_on_runs']==8
    assert art['ordinary_audio_and_guest_identical_across_sources'] and not art['staging_or_timing_gameplay_changed']
    assert len(art['ppu_oracles'])==8 and all(r['frames']==333 and r['native_pixel_mismatches']==0 for r in art['ppu_oracles'])
    assert len(art['palette_pictures'])==4 and all(r['exact_palette_pixel_mapping'] for r in art['palette_pictures'])
    assert len(art['graphics_changed_playing_continuation'])==4
    assert art['catalog_sha256']==digest(ROOT/'build/pride-sprites/catalog.json')
    ui=read('pride-death-art-switch/report.json')
    assert ui['both_sources_both_directions'] and not ui['original_loader_restarted']
    assert ui['matching_graphics_compatible_slot_restored_twice']
    timing=read('pride-death-timeline/report.json','STREAMS_EQUAL_STAGING_DIFFERENT_ADAPTER_OPEN')
    assert timing['unique_death_pose_records']==20 and timing['death_stream_tokens']==33
    assert timing['native_full_stream_field_checks']==1120 and timing['md_live_stream_field_checks']==1800
    assert timing['md_steering_axis_checks']==3216 and not timing['production_death_source_enabled']
    for name,sha in timing['source_sha256'].items():assert digest(ROOT/name)==sha,name
    retained=read('pride-game-over-latest.json','PARTIAL')
    result={'result':'PARTIAL','scope':__doc__,'player_sha256':ph,'headless_sha256':hh,
            'reports_sha256':reports,'unique_death_art_frames':20,'death_stream_entries':33,
            'native_ppu_pixel_oracles':8,'ordinary_death_art_runs':8,
            'original_timing_difference_documented':True,'death_gameplay_source_enabled':False,
            'retained_gates':retained,'full_first_level_fidelity_complete':False,
            'remaining':timing['remaining']+retained['remaining']}
    (ROOT/'build/pride-death-art-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Pride death artwork verified on current binaries; full fidelity remains PARTIAL',flush=True)


if __name__=='__main__':main()
