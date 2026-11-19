"""Bind the revival artwork component and current retained Pride gates."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_owned_death_art


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_owned_death_art.main()
    path=ROOT/'build/pride-revival-scene/report.json';model=json.loads(path.read_text())
    assert model['result']=='PASS' and model['completed_original_video_fields']==783
    assert model['paired_revival_frames']==12 and model['paired_idle_frames']==1
    assert model['cross_process_saved_fields']==783 and model['continuation_fields_per_record']==100
    assert model['model2_records_rejected'] and model['production_binaries_unchanged'] and not model['production_controller_enabled']
    assert model['player_sha256']==digest(ROOT/'dist/LionKing.exe')
    assert model['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe')
    assert model['test_sha256']==digest(ROOT/'engine/build-win/tlk_revival_scene_test.exe')
    folder=path.parent
    assert model['saved_records_sha256']==digest(folder/'records.bin')
    default_path=ROOT/'build/pride-default-death-reference/report.json';default=json.loads(default_path.read_text())
    mappings={'script':ROOT/'tools/verify_pride_revival_scene.py','reference':ROOT/'build/pride-revival-art/reference.json',
        'catalog':ROOT/'build/pride-sprites/catalog.json','default':ROOT/'build/pride-default-death-reference/report.json',
        'default_fields':default_path.parent/str(default['selected_prefix_fields'])/'fields.json','fixture':folder/'original-revival.csv',
        'controller':ROOT/'engine/runner/tlk_death_scene.c','header':ROOT/'engine/runner/tlk_death_scene.h',
        'unit':ROOT/'engine/tests/revival_scene_test.c','legacy':folder/'model2-record.bin'}
    for key,file in mappings.items():assert model['source_sha256'][key]==digest(file),key
    for name,sha in model['logs_sha256'].items():assert sha==digest(folder/name),name
    reference=json.loads(mappings['reference'].read_text())
    assert reference['source_sha256']['script']==digest(ROOT/'tools/pride_revival_art_reference.py')
    assert reference['source_sha256']['fields']==digest(ROOT/'build/pride-revival-art/fields.json')
    for picture in reference['pictures']:
        assert picture['sha256']==digest(ROOT/f"build/pride-revival-art/age-{picture['age']}.png")
    parent_path=ROOT/'build/pride-owned-death-art-latest.json';parent=json.loads(parent_path.read_text())
    assert parent['result']=='PARTIAL' and not parent['full_first_level_fidelity_complete']
    result={'result':'PARTIAL','scope':__doc__,'player_sha256':model['player_sha256'],'headless_sha256':model['headless_sha256'],
        'paired_revival_poses':12,'paired_idle_poses':1,'original_video_fields':783,'new_process_records':783,
        'continuation_fields_per_record':100,'checkpoint_hold_animation_implemented':True,
        'default_idle_path_implemented':True,'controller_model_revision':3,'production_controller_enabled':False,
        'full_first_level_fidelity_complete':False,'source_sha256':{'script':digest(Path(__file__)),
            'revival_component':digest(path),'retained_current_player_gates':digest(parent_path)},
        'remaining':['Connect original native entry/reload/return ownership to the video clock',
                     'Prepare checkpoint data and replacement actor before original MD phase deadlines',
                     'Render mixed-source revival art and fades with checkpoint-owned coordinates',
                     'Integrate independent audio and source-aware outer game saves; verify Windows/F12/interruptions']+parent['remaining']}
    (ROOT/'build/pride-revival-scene-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Checkpoint/default revival artwork and retained player gates verified; full Pride fidelity remains PARTIAL',flush=True)


if __name__=='__main__':main()
