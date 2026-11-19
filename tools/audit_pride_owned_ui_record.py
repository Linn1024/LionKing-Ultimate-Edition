"""Separate the measured nonvisual draw count from owned save pixel/state data."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def canonical_record(path):
    data=bytearray(path.read_bytes());assert data[:8]==b'PRHSAVE1'
    expected=bytes(data[56:88]);data[56:88]=bytes(32)
    assert hashlib.sha256(data).digest()==expected,'Outer integrity'
    assert data[-32:-24]==b'PRPEND01'
    native,history,cache=struct.unpack_from('<III',data,len(data)-24)
    assert len(data)==768+native+history+cache+32
    start=768+native;record=bytearray(data[start:start+history])
    assert record[:8]==b'PRHHIST1' and struct.unpack_from('<I',record,12)[0]==history
    expected=bytes(record[48:80]);record[48:80]=bytes(32)
    assert hashlib.sha256(record).digest()==expected,'History integrity'
    # history_body encodes seven context scalars, then width/column/y/flip,
    # then the draw counter. No image, mask, palette, clock or guest byte is
    # discarded. The live F1 follows Present; scripted save precedes Present.
    offset=96+11*4;draws=struct.unpack_from('<I',record,offset)[0]
    record[offset:offset+4]=bytes(4);data[start:start+history]=record
    return bytes(data),draws,start+offset


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md-media'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-raster-state/live';old=base/'owned-ui-save'/args.case
    old_path=old/'report.json';r=bound(old_path)
    assert r['checks']['whole_ui_free_record'] is False
    assert all(v for k,v in r['checks'].items() if k!='whole_ui_free_record'),r['checks']
    a,draws_a,offset_a=canonical_record(old/'live/tlk_slot1.state')
    b,draws_b,offset_b=canonical_record(old/'control/explicit.state')
    out=base/'owned-ui-save-audit'/args.case;out.mkdir(parents=True,exist_ok=True)
    checks=dict(prior_game_audio_scene_checks=all(v for k,v in r['checks'].items() if k!='whole_ui_free_record'),
        record_integrity=True,all_guest_audio_cache_and_visual_state_equal=a==b,
        only_one_extra_present_count=draws_a==draws_b+1,matching_counter_offset=offset_a==offset_b)
    paths=(Path(__file__),old_path,ROOT/'tools/pride_repeat_state_wide.c',ROOT/'tools/pride_repeat_render_wide.c')
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,
        live_draws=draws_a,scripted_draws=draws_b,counter_file_offset=offset_a,
        native_and_visual_record_bytes_compared=len(a)-68,
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        binary_sha256=r['binary_sha256'],dll_sha256=r['dll_sha256'],
        preceding_strict_byte_comparison='INCOMPLETE: one extra live presentation count and its two validated checksums; no visual/guest/audio/cache difference',
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(args.case,result['result'],checks,draws_a,draws_b,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
