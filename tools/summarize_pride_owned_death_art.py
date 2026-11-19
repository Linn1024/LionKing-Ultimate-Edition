"""Bind the player's owned native death art with current phase/controller gates."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_death_art
import summarize_pride_death_phases
import summarize_pride_death_controller


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_death_art.main()
    summarize_pride_death_phases.main()
    summarize_pride_death_controller.main()
    path=ROOT/'build/pride-owned-death-art/report.json';owned=json.loads(path.read_text())
    assert owned['result']=='PASS' and owned['native_frames']==owned['md_frames']==20
    assert owned['indexed_pixels_per_source']==42204
    assert owned['live_bank_not_required_for_owned_art'] and owned['controller_age0_native_art']
    assert owned['source_buffers_detached'] and owned['rebind_clear_and_corruption_guards']
    assert owned['test_sha256']==digest(ROOT/'engine/build-win/tlk_death_art_test.exe')
    mappings={'script':ROOT/'tools/verify_pride_owned_death_art.py','catalog':ROOT/'build/pride-sprites/catalog.json',
              'golden':ROOT/'build/pride-owned-death-art/original-bitmaps.bin','sprites':ROOT/'engine/runner/tlk_md_sprites.c',
              'header':ROOT/'engine/runner/tlk_md_sprites.h','unit':ROOT/'engine/tests/death_art_test.c'}
    for key,file in mappings.items():assert owned['source_sha256'][key]==digest(file),key
    for name,sha in owned['logs_sha256'].items():assert digest(ROOT/'build/pride-owned-death-art'/name)==sha,name
    art_path=ROOT/'build/pride-death-art/report.json';art=json.loads(art_path.read_text())
    assert art['result']=='PASS' and art['owned_native_frame_rendering_verified']
    audio_path=ROOT/'build/pride-owned-death-audio/report.json';audio=json.loads(audio_path.read_text())
    assert audio['result']=='PASS' and len(audio['ordinary_runs'])==4 and len(audio['graphics_changed_continuations'])==2
    assert audio['player_sha256']==digest(ROOT/'dist/LionKing.exe')
    for key,file in {'script':ROOT/'tools/verify_pride_owned_death_audio.py',
                     'music_report':ROOT/'build/pride-health-death-music/report.json',
                     'reference_wav':ROOT/'build/pride-health-death-music/both-aot/route.wav',
                     'renderer':ROOT/'engine/runner/tlk_wide.c','sprites':ROOT/'engine/runner/tlk_md_sprites.c'}.items():
        assert audio['source_sha256'][key]==digest(file),key
    controller_path=ROOT/'build/pride-death-controller-latest.json';controller=json.loads(controller_path.read_text())
    assert controller['result']=='PARTIAL' and not controller['production_controller_enabled']
    for name in ('native','palette'):
        for mode in ('aot','lle'):
            coverage=json.loads((ROOT/f'build/pride-death-art/{name}-{mode}/coverage.json').read_text())
            assert coverage['owned_native_death_frames']==coverage['seen_owned_native_death_frames']==20
    result={'result':'PARTIAL','scope':__doc__,'player_sha256':digest(ROOT/'dist/LionKing.exe'),
            'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'owned_native_death_rendering_in_player':True,'early_owned_art_ready_before_live_bank':True,
            'native_md_frames':20,'original_indexed_pixels_per_source':42204,
            'native_original_ppu_oracles':8,'ordinary_frame_palette_runs':8,
            'mixed_audio_art_runs':4,'mixed_audio_graphics_changed_saved_continuations':2,
            'source_buffers_detached':True,'native_cache_invalidated_on_resource_rebind':True,
            'production_death_gameplay_source_enabled':False,'full_first_level_fidelity_complete':False,
            'source_sha256':{'script':digest(Path(__file__)),'owned_art':digest(path),'ordinary_art':digest(art_path),
                             'retained_controller_and_phase_gates':digest(controller_path),'combined_audio_art':digest(audio_path),
                             'renderer':digest(ROOT/'engine/runner/tlk_wide.c'),'resources':digest(ROOT/'engine/runner/tlk_resources.c')},
            'remaining':controller['remaining']}
    (ROOT/'build/pride-owned-death-art-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Player-owned native death art and early data availability verified; full Pride fidelity remains PARTIAL',flush=True)


if __name__=='__main__':main()
