"""Bind native CPU readiness/return ownership without closing full Pride fidelity."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
import summarize_pride_scene_prepare


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summarize_pride_scene_prepare.main()
    reports={};paths={}
    for host,binary in (('headless','probe'),('sdl','sdl')):
        path=ROOT/f'build/pride-scene-owner-{host}/report.json';report=json.loads(path.read_text())
        assert report['result']=='CPU_PREPARATION_TIMING_VERIFIED_RENDER_AUDIO_HEALTH_OPEN'
        assert report['sources']==['native','both'] and report['modes']==['control','scheduled']
        assert not report['production_death_behavior_enabled'] and not report['full_first_level_fidelity_complete']
        assert report['probe_sha256']==digest(ROOT/f'engine/build-win/tlk_scene_owner_{binary}.exe')
        for name,sha in report['source_sha256'].items():assert digest(ROOT/name)==sha,name
        for case,run in report['runs'].items():
            for name,sha in run['artifacts_sha256'].items():assert sha==digest(path.parent/case/name),(host,case,name)
        for source in ('native','both'):
            control=report['runs'][source+'-control'];scheduled=report['runs'][source+'-scheduled']
            assert (control['native_actor_age'],control['normal_age'])==(405,469)
            assert scheduled['native_actor_age']<=254 and scheduled['normal_age']==345
            assert scheduled['balanced_native_wait_calls']==29 and scheduled['original_md_revival_art_and_timer_fields']==75
            assert scheduled['native_health_age']==225 and not scheduled['backend_health_matches_md_clock']
        if host=='sdl':
            assert report['runs']['both-scheduled']['level_music_handoff_age']==345
            assert report['runs']['both-scheduled']['md_music_program_sequence'][-2:]==[430,137]
        reports[host]=report;paths[host]=path
    parent_path=ROOT/'build/pride-scene-prepare-latest.json';parent=json.loads(parent_path.read_text())
    assert parent['result']=='PARTIAL' and not parent['full_first_level_fidelity_complete']
    result={'result':'PARTIAL','scope':__doc__,'production_sha256':parent['production_sha256'],
        'cpu_readiness_cases':8,'scheduled_original_art_and_timer_fields':300,
        'native_actor_readiness_age':254,'normal_entry_age':345,'backend_health_restore_age':225,
        'md_checkpoint_health_restore_age':270,'balanced_native_wait_calls_per_schedule':29,
        'md_level_music_handoff_age':345,'idle_timer_handoff_verified':False,
        'production_death_behavior_enabled':False,'full_first_level_fidelity_complete':False,
        'source_sha256':{'script':digest(Path(__file__)),'headless':digest(paths['headless']),
                         'sdl':digest(paths['sdl']),'retained_gates':digest(parent_path)},
        'remaining':['Defer native health/roar restoration to the scene event; verify every bootstrap writer',
                     'Transfer final idle animation state without the extra normal-entry timer decrement',
                     'Integrate owned full-scene rendering/palettes and verify native/MD audio policies',
                     'Implement compiled-path ownership, player lifecycle/outer saves and actual pause/F12/source changes']+parent['remaining']}
    (ROOT/'build/pride-scene-owner-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('CPU actor254/normal345 and300 revival art/timer fields verified; health/render/audio/player integration remain PARTIAL',flush=True)


if __name__=='__main__':main()
