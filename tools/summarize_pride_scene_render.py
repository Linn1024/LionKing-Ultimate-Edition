"""Bind owned scenery/cub pixel evidence without declaring whole-scene fidelity."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_hud_binding


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_hud_binding.main()
    parent_path=ROOT/'build/pride-hud-binding-latest.json';parent=json.loads(parent_path.read_text())
    reports={};owned=0;compared=0;cases=0
    for host,width,count in (('headless',320,8),('sdl',320,8),('headless',256,8),('sdl',256,4)):
        path=ROOT/f'build/pride-scene-render-{host}-{width}-5400/report.json';r=json.loads(path.read_text())
        assert r['result']=='OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN' and len(r['runs'])==count
        binary=ROOT/f'engine/build-win/tlk_scene_render_{"sdl" if host=="sdl" else "probe"}.exe'
        assert r['probe_sha256']==digest(binary)
        for file,sha in r['source_sha256'].items():assert digest(ROOT/file)==sha,file
        for case,result in r['runs'].items():
            folder=path.parent/case;capture=json.loads((folder/'capture.json').read_text())
            assert capture['execution_completed'] and capture['probe_sha256']==r['probe_sha256']
            for file,sha in capture['source_sha256'].items():assert digest(ROOT/file)==sha,file
            for file,sha in result['artifacts_sha256'].items():assert digest(folder/file)==sha,(host,width,case,file)
            if case.endswith('-owned'):
                assert result['owned_fields']==347 and result['release_age']==346 and result['black_reload_and_restore_verified']
                owned+=1;compared+=result['pixels_compared']
            cases+=1
        reports[f'{host}-{width}']={'path':str(path.relative_to(ROOT)),'sha256':digest(path)}
    assert (cases,owned,compared)==(28,14,318373888)
    path=ROOT/'build/pride-scene-render-windows/report.json';window=json.loads(path.read_text())
    assert window['result']=='PASS' and len(window['runs'])==4
    assert window['probe_sha256']==digest(ROOT/'engine/build-win/tlk_scene_render_sdl.exe')
    for file,sha in window['source_sha256'].items():assert digest(ROOT/file)==sha,file
    for case,result in window['runs'].items():
        assert result['actual_window_matches_owned_pixels'] and result['identical_duplicate_presentations']==1
        for file,sha in result['artifacts_sha256'].items():assert digest(path.parent/case/file)==sha,(case,file)
    reports['active_windows']={'path':str(path.relative_to(ROOT)),'sha256':digest(path)}
    ninja=(ROOT/'engine/build-win/build.ninja').read_text()
    default=next(line for line in ninja.splitlines() if line.startswith('build all:'))
    assert 'tlk_scene_render_' not in default
    result=dict(result='PARTIAL',scope=__doc__,production_sha256=parent['production_sha256'],
        scene_pixel_cases=cases,owned_cases=owned,owned_fields_per_case=347,independently_compared_pixels=compared,
        actual_active_windows=4,actual_window_pixels_compared=4*640*448,
        canonical_cpu_ready_age=345,native_pixel_exact_handoff_age=346,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False,
        complete_hud_npc_revival_ownership=False,compiled_scene_ownership=False,
        probe_reports=reports,retained_production_gates={'path':str(parent_path.relative_to(ROOT)),'sha256':digest(parent_path)},
        source_sha256={'script':digest(Path(__file__))},remaining=[
            'Audit original MD SAT and native per-field OAM/metadata at268..298; zero submitted pieces is not zero visible sprites',
            'Prepare correct HUD/NPC presentation and health/roar widget state before first revival visibility',
            'Verify remaining original MD object priority, placement and source-specific scene presentation',
            'Activate the private renderer for fully native graphics at256 in the SDL host when integrating the behavior choice',
            'Implement reusable scene lifetime, active saves, pause/reset/source switching and compiled ownership',
            'Verify boundary input, default/final-life paths and native audio policy/phase'
        ]+parent['remaining'])
    (ROOT/'build/pride-scene-render-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('28 scene cases,318373888 owned pixels and four exact active Windows captures verified; HUD/NPC/full Pride remain PARTIAL',flush=True)


if __name__=='__main__':main()
