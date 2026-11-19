"""Summarize the retained Full Genesis diagnostic window without declaring fidelity complete."""
import argparse
import json
from collections import Counter
from pathlib import Path


def summarize(path, latest_session=False):
    files = [Path(str(path) + f'.{n}') for n in (3, 2, 1)] + [path]
    files = [p for p in files if p.is_file()]
    if not files:
        raise FileNotFoundError(f'No fallback log at {path}')
    groups, kinds, builds, incomplete = {}, Counter(), set(), []
    first_type = None
    frame_records = 0
    session = None
    session_complete = False
    for p in files:
        for line_number, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                incomplete.append(f'{p.name}:{line_number}')
                continue
            if first_type is None:
                first_type = row.get('type')
            if row.get('type') == 'session_start':
                if latest_session:
                    groups, kinds, builds, incomplete = {}, Counter(), set(), []
                    frame_records = 0
                    first_type = 'session_start'
                session = {k: row.get(k) for k in ('pid', 'time', 'build')}
                session_complete = False
            if row.get('type') == 'session_end':
                session_complete = True
            if row.get('build'):
                builds.add(row['build'])
            frame_records += row.get('type') == 'frame'
            if row.get('type') != 'event':
                continue
            kind = row.get('kind', 'unknown')
            kinds[kind] += 1
            key = tuple(row.get(k, '') for k in ('kind', 'resource', 'reason', 'pose', 'caller', 'scene'))
            sprite = row.get('sprite_context', {})
            # Reused RAM pose addresses must not merge unrelated drawings.
            key += tuple(sprite.get(k, '') for k in ('captured_descriptor', 'latched_action',
                'mapped_md_pose', 'first_sample_tile_fnv32', 'first_sample_palette_fnv32',
                'latched_ram_pose_header_fnv32'))
            group = groups.setdefault(key, {
                **dict(zip(('kind', 'resource', 'reason', 'pose', 'caller', 'scene'), key)),
                'records': 0, 'occurrences': 0, 'first_field': row['field'],
                'last_field': row['field'], 'levels': set(),
                'example_object': row.get('object'), 'example_detail': row.get('detail'),
                'example_sprite_context': sprite or None,
            })
            group['records'] += 1
            group['occurrences'] += row.get('occurrences', 1)
            group['first_field'] = min(group['first_field'], row['field'])
            group['last_field'] = max(group['last_field'], row['field'])
            group['levels'].add(row.get('level'))
    for group in groups.values():
        group['levels'] = sorted(v for v in group['levels'] if v is not None)
    return {
        'files': [str(p) for p in files], 'builds': sorted(builds),
        'older_history_rotated': first_type == 'rotation',
        'incomplete_records': incomplete, 'frame_records': frame_records,
        'event_records_by_kind': dict(kinds),
        'confirmed_fallback_records': kinds['fallback'],
        'scope': 'latest_session' if latest_session else 'retained_history',
        'latest_session': session,
        'latest_session_complete': session_complete,
        'full_game_no_fallback_verdict': 'not_assessed',
        'note': 'Sampling failures and unclassified paths need source/visibility review; '
                'coverage gaps are inventory, not demonstrated runtime failures. '
                'Counts measure visits/samples, including repeated compositor passes.',
        'events': sorted(groups.values(), key=lambda g: (-g['records'], g['resource'], g['reason'])),
    }


def readable(result):
    lines = ['Full Genesis fallback report',
             f"Scope: {result['scope']}; frames logged: {result['frame_records']}",
             f"Confirmed fallback records: {result['confirmed_fallback_records']}",
             'Requirement: no SNES asset fallbacks when MD is selected.',
             'Candidates below need review; this is not a whole-game clean verdict.']
    if result['older_history_rotated']:
        lines.append('WARNING: earlier history was rotated out.')
    if result['incomplete_records']:
        lines.append(f"WARNING: {len(result['incomplete_records'])} incomplete/invalid log lines.")
    if not result['latest_session_complete']:
        lines.append('Session still running, interrupted, or missing its end record.')
    for e in result['events']:
        lines.append(f"\n[{e['kind']}] {e['resource']} / {e['reason']}\n"
                     f"  levels={e['levels']} scene={e['scene']} fields={e['first_field']}..{e['last_field']} "
                     f"pose={e['pose']} caller={e['caller']} object={e['example_object']} "
                     f"records={e['records']} occurrences={e['occurrences']}")
        s = e.get('example_sprite_context')
        if s:
            lines.append(f"  owner={s['captured_descriptor']} action={s['latched_action']} "
                         f"world={s['latched_actor_xy']} camera={s['camera_xy']} "
                         f"screen={s['first_sample_screen_xy']}\n"
                         f"  requested frames={s['requested_frames']} palette={s['requested_palette']}; "
                         f"MD frame={s['mapped_md_pose']} mapped/accepted roles={s['mapped_role']}/{s['scene_role']} "
                         f"image ready={s['image_ready']}\n"
                         f"  drawing={s['first_sample_tile_fnv32']} palette={s['first_sample_palette_fnv32']} "
                         f"RAM header={s['latched_ram_pose_header_fnv32']}")
    if not result['events']:
        lines.append('No events in the retained scope. Unvisited paths remain unverified.')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', nargs='?', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'build/logs/full-genesis-fallbacks.jsonl')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--latest-session', action='store_true')
    parser.add_argument('--text', action='store_true', help='Print a readable investigation list.')
    args = parser.parse_args()
    report = summarize(args.log, args.latest_session)
    result = readable(report) if args.text else json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(result + '\n', encoding='utf-8')
    else:
        print(result)


if __name__ == '__main__':
    main()
