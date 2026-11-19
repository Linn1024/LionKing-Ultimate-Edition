"""Retain all owned save data while identifying a nonvisual draw-count difference."""
import argparse
import json
from pathlib import Path

from audit_scenes import ROOT
from audit_pride_owned_ui_record import canonical_record
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md-media'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-singlepass';raw_path=base/'owned-ui-save'/args.case/'report.json';raw=bound(raw_path)
    assert all(v for k,v in raw['checks'].items() if k!='whole_ui_free_record')
    a,draw_a,offset_a=canonical_record(raw_path.parent/'live/tlk_slot1.state')
    b,draw_b,offset_b=canonical_record(raw_path.parent/'control/explicit.state')
    checks=dict(prior_checks=all(v for k,v in raw['checks'].items() if k!='whole_ui_free_record'),
                same_format_offset=offset_a==offset_b,all_guest_audio_pixels_masks_context=a==b,
                only_nonvisual_draw_count=abs(draw_a-draw_b)<=1)
    assert all(checks.values()),checks
    out=base/'owned-ui-save-audit'/args.case;out.mkdir(parents=True)
    paths=[Path(__file__),ROOT/'tools/audit_pride_owned_ui_record.py',raw_path]
    report=dict(result='PASS',checks=checks,draw_counts=[draw_a,draw_b],canonical_bytes=len(a),binary_sha256=raw['binary_sha256'],
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,'PASS owned UI-free data',checks,draw_a,draw_b,flush=True)


if __name__=='__main__':main()
