"""Index current streaming-margin evidence without declaring Pride complete."""
import hashlib
import json
import re
import subprocess
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe';head=ROOT/'engine/build-win/tlk_headless.exe';evidence={}
    def report(relative,fresh=True):
        path=ROOT/'build'/relative;row=json.loads(path.read_text());assert row['result']=='PASS',relative
        if fresh:assert path.stat().st_mtime>=player.stat().st_mtime,('Stale report',relative)
        if 'player_sha256' in row:assert row['player_sha256']==digest(player),relative
        if 'headless_sha256' in row:assert row['headless_sha256']==digest(head),relative
        evidence[relative]=digest(path);return row
    report('pride-streaming-top-original/report.json',False)
    report('pride-reaction-probability/report.json',False)
    scope_path=ROOT/'build/pride-ambiguous-scope/report.json'
    scope=json.loads(scope_path.read_text())
    assert scope['result']=='GUARDED_PATHS_VERIFIED_GLOBAL_SCOPE_OPEN'
    assert scope['original_cpu_cases']==1114112 and not scope['global_or_indirect_unreachability_proven']
    for name,path in [('oracle_source','tools/pride_animation_scope_oracle.c'),
                      ('oracle_bus_source','tools/pride_terrain_native_oracle.c'),
                      ('interpreter_source','engine/build-win/tlk-runtime/interp816.c'),
                      ('oracle_dll','build/pride_animation_scope.dll')]:
        assert scope['source_sha256'][name]==digest(ROOT/path),('Stale animation scope evidence',name)
    evidence['pride-ambiguous-scope/report.json']=digest(scope_path)
    candidate_path=ROOT/'build/pride-route-candidate/report.json'
    candidate=json.loads(candidate_path.read_text())
    assert candidate['headless_sha256']==digest(head) and candidate['execution_modes_equal']
    assert candidate['result']=='PARTIAL' and not candidate['first_level_completed']
    evidence['pride-route-candidate/report.json']=digest(candidate_path)
    selected=report('pride-streaming-verification/report.json')
    report('pride-streaming-top-switch/report.json')
    report('pride-ceiling-switch/report.json')
    states=report('pride-state-profiles/report.json')
    assert len(states['matching_source_hashes'])==19 and states['mismatches_rejected_before_load']==32
    report('setup-verification/report.json');report('pride-mix-verification/report.json')
    authored={name:report('pride-authored-completion/'+name+'/report.json') for name in ('gameplay','media','gameplay256','media256')}
    assert all(row['normal_first_level_completion_verified'] and not row['loaded_states'] for row in authored.values())
    for name,before in [('play-report.json','streaming-native-before.json'),('allbugs-report.json','streaming-allbugs-before.json')]:
        row=report('native-route-verification/'+name)
        assert row['routes']==json.loads((ROOT/'build'/before).read_text())['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/streaming-allbugs-before.ram').read_bytes()
    install=json.loads((ROOT/'game-data/install.json').read_text())
    assert install['player_sha256']==digest(player) and install['scene_cache']['verified_background_levels']==[0,2]
    log=ROOT/'build/pride-streaming-unit.log'
    with log.open('wb') as output:
        subprocess.run([str(ROOT/'engine/build-win/tlk_streaming_top_test.exe'),str(ROOT/'Lion King, The (USA).sfc')],stdout=output,stderr=subprocess.STDOUT,check=True)
    evidence['pride-streaming-unit.log']=digest(log)
    widths=(ROOT/'build/pride-streaming-exit-mx.log').read_text(encoding='utf-16')
    assert not re.search(r'^WRONG',widths,re.M) and len(re.findall(r'^UNPROVEN',widths,re.M))==11
    result={'result':'PARTIAL','scope':__doc__,'player_sha256':digest(player),'headless_sha256':digest(head),
            'installed_manifest_matches':True,'verified_component_sha256':evidence,
            'native_75_routes_and_60648_allbugs_unchanged':True,'original_vertical_window_cases':1280,
            'original_md_activation_and_contact_positions_observed':True,'matched_initial_integer_position_fields':620,
            'matched_initial_nonlag_integer_position_updates':686,
            'full_pride_fidelity_complete':False,'original_md_derived_route_complete':False,
            'authored_320_gameplay_and_media_complete':True,
            'authored_256_gameplay_and_media_complete':True,
            'original_age_guard_selector_cases':scope['original_cpu_cases'],
            'ambiguous_global_pose_scope_closed':False,
            'exact_authored_320_media_wav_sha256':authored['media']['exact_mixed_wav_sha256'],
            'exact_authored_256_media_wav_sha256':authored['media256']['exact_mixed_wav_sha256'],
            'next_gap':selected['next_gap'],
            'next_gap_explained_by_different_rng_state':True,
            'ordinary_input_candidate_progress':candidate['highest_progress'],
            'remaining':['Broader movement/contact, attack/enemy/difficulty contracts and ambiguous mapping scope',
                         'Full art/audio/unknown-pose and interruption/revival/bonus checklist']}
    (ROOT/'build/pride-streaming-progress-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Streaming component evidence indexed; full Pride fidelity remains PARTIAL',flush=True)


if __name__=='__main__':main()
