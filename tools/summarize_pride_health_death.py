"""Bind the health-death audio milestone while retaining the full Pride goal.

Audio source support does not implement MD death gameplay or prove all first-
level states. This index requires current installed binaries and fresh gates.
"""
import hashlib
import json
import re
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player=ROOT/'dist/LionKing.exe';head=ROOT/'engine/build-win/tlk_headless.exe'
    reports={}
    def read(relative,runtime=True,result='PASS'):
        path=ROOT/'build'/relative;row=json.loads(path.read_text())
        assert row['result']==result,(relative,row['result'])
        if runtime:
            assert path.stat().st_mtime>=player.stat().st_mtime,('Stale report',relative)
            if 'player_sha256' in row:assert row['player_sha256']==digest(player),relative
            if 'headless_sha256' in row:assert row['headless_sha256']==digest(head),relative
        reports[relative]={'sha256':digest(path),'result':row['result']};return row
    original=read('pride-health-death-original/report.json',False)
    read('pride-health-death-original/life-report.json',False)
    assert original['ordinary_power_on'] and not original['loaded_states']
    death=read('pride-health-death-music/report.json')
    assert death['original_reference_sha256']==reports['pride-health-death-original/report.json']['sha256']
    assert len(death['runs'])==4 and death['ordinary_power_on_complete_runs']==8
    assert len(death['exact_saved_phases'])==6 and death['invalid_phase_rejected']
    assert death['living_v1_audio_exact'] and death['legacy_death_loop_repaired']
    timeline=read('pride-death-fx-timeline/report.json')
    assert all(case['exact_timeline_advance'] for case in timeline['cases'].values())
    switch=read('pride-health-death-switch/report.json')
    assert switch['both_directions_persisted'] and switch['original_loader_calls']==3
    read('pride-audio-state/report.json');read('pride-audio-live-state/report.json')
    read('setup-verification/report.json');read('final-music-switch/report.json')
    states=read('pride-state-profiles/report.json')
    assert len(states['matching_source_hashes'])==19 and states['mismatches_rejected_before_load']==32
    authored={name:read('pride-authored-completion/'+name+'/report.json')
              for name in ('gameplay','media','gameplay256','media256')}
    assert all(row['normal_first_level_completion_verified'] and not row['loaded_states'] for row in authored.values())
    assert authored['media']['exact_mixed_wav_sha256']=='5e2d27e16373ea573b5d4ff64f7fdc6836c076f420de12092e934f2c554e1046'
    assert authored['media256']['exact_mixed_wav_sha256']=='4f8c40d94c82e073866536de05cdc80e8236f09ec8b82b8451c38b8a165761e7'
    for name,row in authored.items():
        if row['media']:
            profile=ROOT/'build/pride-authored-completion'/name/'resources.ini'
            assert 'audio.music.pride_health_death = md' in profile.read_text()
    for name in ('play-report.json','allbugs-report.json'):
        row=read('native-route-verification/'+name)
        baseline=json.loads((ROOT/'build/pride-death-music-before'/('baseline-'+name)).read_text())
        assert row['routes']==baseline['routes'],('Native baseline changed',name)
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()==(ROOT/'build/streaming-allbugs-before.ram').read_bytes()
    lifecycle=read('pride-death-lifecycle/report.json',False,'COUNTER_CONVENTIONS_VERIFIED_DEATH_TIMING_OPEN')
    assert not lifecycle['counter_conventions']['raw_write_timing_alone_justifies_life_counter_patch']
    assert lifecycle['native']['health_zero_to_life_loss_fields']==344
    assert lifecycle['md']['health_zero_to_life_loss_fields']==0
    for name,pattern in [('pride-health-death-unit.log','new-process continuation PASS'),
                         ('pride-health-death-pytest.log','23 passed, 4 skipped')]:
        path=ROOT/'build'/name;assert pattern in path.read_text(errors='replace')
        reports[name]={'sha256':digest(path)}
    mx=ROOT/'build/pride-health-death-exit-mx.log';text=mx.read_text(errors='replace')
    assert not re.search(r'^WRONG',text,re.M) and len(re.findall(r'^UNPROVEN',text,re.M))==11
    reports[mx.name]={'sha256':digest(mx),'wrong':0,'existing_unproven':11}
    manifest=json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256']==digest(player)
    assert manifest['scene_cache']['version']==1 and manifest['scene_cache']['verified_background_levels']==[0,2]
    report={'result':'PARTIAL','scope':__doc__,'player_sha256':digest(player),'headless_sha256':digest(head),
            'installed_manifest_matches':True,'reports':reports,
            'independent_health_death_music_verified':True,'native_death_battle_loop_restart_fixed':True,
            'md_hurt_ring_and_resampler_preserved':True,'outer_save_version':4,'audio_envelope_schema':2,
            'audio_schema1_living_compatibility_verified':True,'native_75_routes_and_60648_allbugs_unchanged':True,
            'supported_320_256_mixtures_complete':True,'full_first_level_fidelity_complete':False,
            'remaining':['Independent MD death/life-counter/animation/fade/revival gameplay contract',
                         'Fall deaths, game over and broader audio interruption/source combinations',
                         'Remaining first-level attack/enemy/difficulty contracts',
                         'Global/NPC ambiguous pose scope, remaining artwork/effects/voice events',
                         'Full first-level requirement and mixed-source completion audit']}
    target=ROOT/'build/pride-health-death-latest.json';target.write_text(json.dumps(report,indent=2)+'\n')
    print('Health-death audio and retained current gates indexed; full Pride fidelity remains PARTIAL',flush=True)


if __name__=='__main__':main()
