"""Separate reachable-window evidence from synthetic zero-timer differences."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

out=ROOT/'build/pride-hyena-entrance114';out.mkdir()
proof_paths=[ROOT/'build'/name/'report.json' for name in ('pride-hyena-intro109','pride-battle-music112','pride-hyena-entrance113')]
original,timeline,gates=[bound(p) for p in proof_paths]
frames_path=proof_paths[0].parent/'frames.json';frames=json.loads(frames_path.read_text())
waiting=[r for r in frames if r['action']==0x19b59e]
current_music=int(timeline['battle_music_calls'][0]['field']);current_jump=int(timeline['first_native_weak_jump']['field'])
checks=dict(original_intro_verified=all(original['checks'].values()),current_guest_neutral_timeline=all(timeline['checks'].values()),
    all5040_original_decisions_characterized=gates['fixtures']==5040 and gates['groups']==dict(equal=4872,timer_zero_underflow=72,camera_window=96,unexplained=0),
    observed_original_md_waiting_timer_always_positive=bool(waiting) and all(r['timer']>0 for r in waiting),
    original_md_music_and_first_jump_same_field=int(original['battle_music_calls'][0]['frame'])==original['first_weak_jump']['field']==3951,
    current_battle_command_three_fields_before_native_jump=current_jump-current_music==3)
paths=[Path(__file__),*proof_paths,frames_path]
(out/'report.json').write_text(json.dumps(dict(result='ENTRANCE_AND_MUSIC_EVIDENCE_QUALIFIED' if all(checks.values()) else 'FAIL',checks=checks,
    current_music_field=current_music,current_jump_field=current_jump,current_battle_command_lead_fields=current_jump-current_music,
    original_md_waiting_samples=len(waiting),original_md_waiting_timer_range=[min(r['timer'] for r in waiting),max(r['timer'] for r in waiting)],
    findings=['Original camera-window width is256 in SNES helper and320 in MD helper; strict bounds with64-pixel margin give96 differing tested countdown decisions.',
              'Synthetic input timer0 gives72 further differences. No timer0 waiting state occurs in this sampled natural MD opening; do not implement this as a generally reachable gameplay difference without interruption/reachability evidence.',
              'Current selected MD battle music command leads current native first weak jump by3 fields. Original MD issues music134 in its first weak-jump field. Routes differ; compare semantic event timing rather than absolute field3951 versus3849.',
              'Gate113 check name all10080_cases is a label error; its formula and retained fixture count5040 are correct.'],
    production_or_capabilities_changed=False,full_first_level_complete=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('Entrance evidence',checks,flush=True)
