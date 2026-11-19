"""Retain the partial original contact comparison with both new sources selected.

Directional hurt-state pairs have separate original-code/entry evidence.
Motion, health and hurt-phase gaps remain explicit differences. This comparison
alone does not prove independent sources, save/yield or full fidelity.
"""
import argparse
import hashlib
from pathlib import Path
import json
from audit_scenes import ROOT
from compare_pride_roll_originals import compare


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'build/pride-activation-reactivation-contacts/snes.json')
    parser.add_argument('--require-match',action='store_true')
    args=parser.parse_args()
    source = args.source
    reference = ROOT/'build/pride-roll-contacts/md.json'
    native = json.loads(source.read_text())
    md = json.loads(reference.read_text())
    assert all(native[k] for k in ('ordinary_native_input_boot', 'md_start_selected', 'md_camera_selected',
                                  'md_activation_selected', 'md_reactivation_selected'))
    assert md['fresh_md_input_boot'] and native['settle_frames'] == md['settle_frames'] == 256
    report = compare(native['cases'], md['cases'], False)
    assert report['total_fields_per_version'] == 1238
    complete = all(r['result'] == 'MATCH' for r in report['cases'].values())
    report.update(result='PASS' if complete else 'PARTIAL', scope=__doc__,
                  full_enemy_fidelity_complete=False, selected_source_aot_lle_parity_checked_here=False,
                  source_sha256={'native': hashlib.sha256(source.read_bytes()).hexdigest(),
                                 'md': hashlib.sha256(reference.read_bytes()).hexdigest()})
    (source.parent/'compare.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Combined-source contact evidence:', report['result'], flush=True)
    if args.require_match:assert complete, 'Original contact differences remain; inspect compare.json'


if __name__ == '__main__':
    main()
