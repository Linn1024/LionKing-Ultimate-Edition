"""Bind checkpoint health/idle ownership while keeping complete Pride fidelity open."""
import json
from pathlib import Path
from audit_scenes import ROOT
from summarize_pride_scene_owner import digest
import summarize_pride_scene_owner


def main():
    summarize_pride_scene_owner.main()
    bound = {}
    for host, binary in (('headless', 'probe'), ('sdl', 'sdl')):
        path = ROOT / f'build/pride-scene-restore-{host}/report.json'
        report = json.loads(path.read_text())
        assert report['result'] == 'RESTORE_AND_HANDOFF_VERIFIED_RENDER_PLAYER_OPEN'
        assert report['sources'] == ['native', 'both'] and report['modes'] == ['control', 'canonical']
        assert report['probe_sha256'] == digest(ROOT / f'engine/build-win/tlk_scene_restore_{binary}.exe')
        for name, sha in report['source_sha256'].items():
            assert digest(ROOT / name) == sha, name
        for case, run in report['runs'].items():
            for name, sha in run['artifacts_sha256'].items():
                assert digest(path.parent / case / name) == sha, (host, case, name)
            if case.endswith('-canonical'):
                assert (run['health_age'], run['normal_age'], run['idle_timer_at_ready']) == (270, 345, 5)
                assert run['actor_age'] <= 254 and run['revival_art_and_timer_fields'] == 76
                assert run['widget_holds'] == 1 and run['canonical_idle_calls'] == 2
        bound[host] = digest(path)
    path = ROOT / 'build/pride-scene-restore-repeat/report.json'
    repeat = json.loads(path.read_text())
    assert repeat['result'] == 'PASS' and set(repeat['runs']) == {'native', 'both'}
    assert repeat['source_sha256']['primary_report'] == bound['sdl']
    assert repeat['source_sha256']['script'] == digest(ROOT / 'tools/verify_pride_restore_repeat.py')
    assert repeat['source_sha256']['restore_coordinator'] == digest(ROOT / 'tools/pride_scene_restore_probe.c')
    assert repeat['probe_sha256'] == digest(ROOT / 'engine/build-win/tlk_scene_restore_sdl.exe')
    for case, run in repeat['runs'].items():
        assert run['exact_guest_window_and_scene_fields'] and run['exact_pcm_bytes'] > 0
        for name, sha in run['artifacts_sha256'].items():
            assert digest(path.parent / case / name) == sha, (case, name)
    parent_path = ROOT / 'build/pride-scene-owner-latest.json'
    parent = json.loads(parent_path.read_text())
    result = dict(result='PARTIAL', scope=__doc__, production_sha256=parent['production_sha256'],
                  checkpoint_cases=8, fresh_windows_repeat_cases=2,
                  canonical_original_revival_fields=304, health_restore_age=270,
                  actor_ready_age=254, normal_entry_age=345, idle_timer_at_ready=5,
                  production_death_behavior_enabled=False, full_first_level_fidelity_complete=False,
                  source_sha256=dict(script=digest(Path(__file__)), headless=bound['headless'],
                                     sdl=bound['sdl'], repeat=digest(path), retained_gates=digest(parent_path)),
                  remaining=[
                      'Rebind HUD meter roles after native task relocation at checkpoint reload',
                      'Verify boundary input, default/final-life and other death contexts',
                      'Integrate owned whole-scene rendering, layers, fades and palette state',
                      'Verify native audio policy/phase; deterministic replay is not source phase equivalence',
                      'Implement compiled ownership, player lifecycle, outer saves, pause/reset/source switching'
                  ] + parent['remaining'][2:])
    (ROOT / 'build/pride-scene-restore-latest.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Checkpoint health270/actor254/normal345/idle5,304 original fields and two exact Windows repeats verified; PARTIAL', flush=True)


if __name__ == '__main__':
    main()
