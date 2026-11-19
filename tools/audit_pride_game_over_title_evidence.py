"""Bind original title input boundary and neutral current-player setup trace."""
import csv
import json
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT / 'build/pride-game-over-title-evidence2'; out.mkdir()
    names = ['pride-game-over-title-input-original/report.json',
             'pride-game-over-title-boundary-original/report.json',
             'pride-game-over-title-setup2/report.json',
             'pride-game-over-bindings/report.json']
    reports = {}; checks = {}; timings = {}
    for name in names:
        reports[name] = bound(ROOT / 'build' / name); checks[name + '_bound'] = True
    original = reports[names[0]]; boundary = reports[names[1]]; observer = reports[names[2]]
    checks['original_routes_unedited'] = all(r['ordinary_route'] and not r['guest_or_rom_edits'] for r in (original, boundary))
    checks['original_single_field_first515'] = boundary['cases']['1']['first_accepted'] == 515
    checks['original_four_field_first512'] = boundary['cases']['4']['first_accepted'] == 512
    checks['original_boundary_all6'] = len(boundary['checks']) == 6 and all(boundary['checks'].values())
    checks['original_start700_changes_title'] = original['cases']['start700']['first_sample_picture_differs_from_neutral'] is not None
    checks['observer_all8_neutral'] = observer['result'] == 'NEUTRAL' and len(observer['checks']) == 8 and all(observer['checks'].values())
    base = ROOT / 'build/pride-game-over-title-setup2'
    checks['observer_binary'] = digest(base / 'player.exe') == observer['binary_sha256']
    checks['observer315_link_inputs'] = len(observer['link_inputs_sha256']) == 315 and all(digest(ROOT / p) == sha for p, sha in observer['link_inputs_sha256'].items())
    for width in (256, 320):
        rows = list(csv.reader((base / str(width) / 'title.csv').open()))
        points = [r for r in rows if r[0] == 'point' and 343 <= int(r[1]) <= 463]
        starts = [r for r in points if r[2] == 'c1ccfe']
        ends = [r for r in points if r[2] == 'c1cd85']
        pairs = []
        for begin, end in zip(starts, ends):
            pairs.append(dict(source=begin[4], destination=begin[5], start=int(begin[1]),
                              end=int(end[1]), source_end=end[4], destination_end=end[5]))
        checks[f'{width}_ten_decoder_pairs'] = len(starts) == len(ends) == 10 and all(p['start'] <= p['end'] for p in pairs)
        before = next(int(r[1]) for r in points if r[2] == 'c082a5')
        after = next(int(r[1]) for r in points if r[2] == 'c082bb')
        checks[f'{width}_sound_upload_gap65'] = after - next(p['end'] for p in pairs if p['source'] == 'ed8d99') == 65
        frames = [r for r in rows if r[0] == 'frame']
        first = next(int(r[1]) for r in frames if r[3] == 'c005ab' and int(r[12]))
        checks[f'{width}_first_title463'] = first == 463
        checks[f'{width}_native_intro_still_phase4_at700'] = any(r[0] == 'point' and r[1:3] == ['700', 'c463fc'] and r[10] == '4' for r in rows)
        timings[str(width)] = dict(audio_load_entry=before, audio_load_exit=after,
                                  decoder_pairs=pairs, summed_decoder_field_spans=sum(p['end']-p['start'] for p in pairs),
                                  first_title_picture=first,
                                  note='Observed intervals overlap setup work; no promise that subtracting them reproduces MD timing.')
    checks['framework_submodules_unmodified'] = not subprocess.check_output(['git', 'status', '--porcelain', '--', 'snesrecomp', 'recomp-ui'], cwd=ROOT / 'engine', text=True).strip()
    paths = [Path(__file__), *[ROOT / 'build' / n for n in names]]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, timings=timings,
                  scope='Research evidence only: title delay/input remain unfixed; no capability or public player change.',
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], sum(checks.values()), '/', len(checks), flush=True)
    assert all(checks.values())


if __name__ == '__main__': main()
