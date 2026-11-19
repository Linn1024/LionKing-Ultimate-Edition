"""Compare installed playback with the retained preceding uncached mixed route."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    base = ROOT/'build/pride-installed-cache41'
    out = base/'transparency'
    out.mkdir()
    old_path = ROOT/'build/pride-porcupine38/complete-wide/report.json'
    old = bound(old_path)
    actual_path = base/'verification/report.json'
    actual = bound(actual_path)
    assert old['result'] == actual['result'] == 'PASS'
    before = old_path.parent
    after = base/'verification/full-aot'
    checks = dict(retained_uncached_command='--asset-cache' not in old['command'],
                  final_picture_and_full_wram=hashes(before/'run.log') == hashes(after/'run.log'))
    for name in ('window.png', 'scene.json', 'attack.csv', 'events.csv', 'tree.jsonl'):
        checks[name+'_unchanged'] = digest(before/name) == digest(after/name)
    previous_audio = pcm(before/'audio.wav')
    current_audio = pcm(after/'audio.wav')
    checks['entire_retained_80_second_pcm_prefix_exact'] = current_audio[:len(previous_audio)] == previous_audio
    checks['new_capture_also_covers_the_rest_of_the_route'] = len(current_audio) > len(previous_audio)
    paths = [Path(__file__), old_path, actual_path]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  old_capture_pcm_bytes=len(previous_audio), new_capture_pcm_bytes=len(current_audio),
                  previous_pcm_capped_at_80_seconds=True, whole_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
