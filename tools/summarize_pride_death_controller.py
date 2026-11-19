"""Bind the implemented scene controller and its original field/return evidence."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source=ROOT/'build/pride-death-controller/report.json';model=json.loads(source.read_text());assert model['result']=='PASS'
    player=ROOT/'dist/LionKing.exe';headless=ROOT/'engine/build-win/tlk_headless.exe'
    assert model['player_sha256']==digest(player) and model['headless_sha256']==digest(headless)
    assert model['controller_test_sha256']==digest(ROOT/'engine/build-win/tlk_death_scene_test.exe')
    mappings={'script':ROOT/'tools/verify_pride_death_controller.py','timeline':ROOT/'build/pride-death-timeline/report.json',
              'revival_reference':ROOT/'build/pride-revival-reference/report.json',
              'default_reference':ROOT/'build/pride-default-death-reference/report.json',
              'poses':ROOT/'build/pride-death-controller/original-fields.csv',
              'palettes':ROOT/'build/pride-death-controller/original-palettes.csv',
              'phases':ROOT/'build/pride-death-controller/original-phases.csv',
              'controller':ROOT/'engine/runner/tlk_death_scene.c','header':ROOT/'engine/runner/tlk_death_scene.h',
              'unit':ROOT/'engine/tests/death_scene_test.c'}
    for key,path in mappings.items():assert model['source_sha256'][key]==digest(path),key
    for name,sha in model['logs_sha256'].items():assert digest(ROOT/'build/pride-death-controller'/name)==sha
    assert model['original_pose_motion_fields']==2242 and model['original_palette_word_checks']==196416
    assert model['original_phase_field_checks']==3070 and model['cross_process_saved_phases']==45
    assert model['scene_record_bytes']==128 and model['scene_record_atomic_rejection']
    assert model['checkpoint_ready_age']==345 and model['default_ready_age']==300
    assert model['checkpoint_health_age']==270 and model['default_health_age']==274
    assert model['checkpoint_respawn_hold_fields']==49 and model['palette_settled_does_not_end_scene']
    assert model['production_binaries_unchanged'] and not model['production_controller_enabled']
    previous_path=ROOT/'build/pride-death-phases-latest.json';previous=json.loads(previous_path.read_text())
    assert previous['result']=='PARTIAL' and previous['player_sha256']==model['player_sha256'] and previous['headless_sha256']==model['headless_sha256']
    result={'result':'PARTIAL','scope':__doc__,'player_sha256':model['player_sha256'],'headless_sha256':model['headless_sha256'],
            'native_scene_controller_implemented':True,'production_controller_enabled':False,'production_binaries_changed':False,
            'original_pose_motion_fields':2242,'original_palette_words':196416,'original_phase_fields':3070,
            'cross_process_saved_phases':45,'checkpoint_normal_play_age':345,'default_normal_play_age':300,
            'checkpoint_respawn_hold_fields':49,'full_first_level_fidelity_complete':False,
            'source_sha256':{'script':digest(Path(__file__)),'controller_verification':digest(source),'retained_phase_evidence':digest(previous_path)},
            'remaining':['Connect the owned clock to original native entry/exit and checkpoint preparation',
                         'Render early death poses and selective fades with independent SNES/MD resources',
                         'Commit actor/health/final-life events with independent audio and source-aware outer saves',
                         'Verify ordinary player routes, actual windows, F12 and interruption behavior before enabling the option']+previous['remaining']}
    (ROOT/'build/pride-death-controller-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Native death controller and both revival return paths verified; runtime integration remains open',flush=True)


if __name__=='__main__':main()
