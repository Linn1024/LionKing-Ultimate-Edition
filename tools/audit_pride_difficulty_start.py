"""Bind the six ordinary difficulty starts and compare their starting resources.

This does not establish enemy behavior, damage, retries or complete difficulty
equivalence. Menu labels and actual Windows clients require visual inspection.
"""
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import ROOT
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound


def main():
    base = ROOT/'build/pride-difficulty-start2'
    out = base/'comparison'
    out.mkdir(exist_ok=False)
    reports = {s:bound(base/s/'report.json') for s in ('snes', 'md')}
    checks = {}
    for source, report in reports.items():
        checks[source+'_ordinary_unedited'] = (report['ordinary_power_on'] and
            not report['loaded_states'] and not report['guest_or_rom_edits'])
    rows = {}
    for name, spare in [('easy', 8), ('normal', 2), ('hard', 0)]:
        snes = reports['snes']['observations'][name]
        md = reports['md']['observations'][name]
        ram = (base/'md'/name/'wram.bin').read_bytes()
        checks[name+'_md_raw_record'] = (struct.unpack_from('<H', ram, 0xccee)[0] == md['lives']
            and struct.unpack_from('<H', ram, 0xccf6)[0] == md['health'])
        scene = json.loads((base/'snes'/name/'scene.json').read_text())['latched_gameplay']
        checks[name+'_snes_display_record'] = (scene['lives'] == snes['lives'] and scene['health'] == snes['health'])
        checks[name+'_initial_health'] = snes['health'] == md['health'] == 4
        checks[name+'_life_accounting'] = snes['lives'] == md['lives']-1 == spare
        rows[name] = dict(health=4, snes_spare_lives=snes['lives'], md_total_lives=md['lives'])
    assert all(checks.values()), checks
    paths = [Path(__file__), ROOT/'tools/capture_pride_difficulty_start.py',
             ROOT/'tools/summarize_pride_practice.py',
             *[base/s/'report.json' for s in reports]]
    result = dict(result='BOUNDED_STARTING_RESOURCES_MATCH', checks=checks,
                  observations=rows, scope=__doc__, full_difficulty_equivalence=False,
                  implementation_change_needed_for_starting_resources=False,
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['result'], len(checks), 'checks', flush=True)


if __name__ == '__main__':
    main()
