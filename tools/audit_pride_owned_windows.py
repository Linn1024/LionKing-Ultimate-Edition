"""Audit cross-mode owned loads at canonical bank clocks, after APU catch-up."""
import argparse
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import read_rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md-media'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-raster-state/verified';old=base/'windows-owned'/args.case;old_path=old/'report.json';r=bound(old_path)
    assert r['result']=='INCOMPLETE' and not r['checks']['bank-clock.csv']
    assert all(v for k,v in r['checks'].items() if k!='bank-clock.csv'),r['checks']
    expected=[row for row in read_rows(old/'baseline/bank-clock.csv') if int(row['field'])>r['saved_field']]
    actual=read_rows(old/'resumed/bank-clock.csv');canonical=('field','pc','master','port_after')
    differences=[dict(field=a['field'],columns=[k for k in a if a[k]!=b[k]],before=a,after=b) for a,b in zip(expected,actual) if a!=b]
    checks=dict(all_guest_audio_scene_client_checks=all(v for k,v in r['checks'].items() if k!='bank-clock.csv'),
        bank_count=len(actual)==len(expected)==2,
        bank_instruction_and_post_catchup_clock=[[row[k] for k in canonical] for row in actual]==[[row[k] for k in canonical] for row in expected],
        only_tier_dependent_pre_catchup_values=all(set(d['columns'])<= {'pending_before','port_before'} for d in differences),
        monotonic_catchup=all(int(row['port_before'])<=int(row['port_after']) for row in actual+expected))
    out=base/'windows-owned-audit'/args.case;out.mkdir(parents=True,exist_ok=True)
    paths=(Path(__file__),old_path,ROOT/'tools/pride_repeat_bank.c')
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,
        binary_sha256=r['binary_sha256'],dll_sha256=r['dll_sha256'],native_fields_compared=r['native_fields_compared'],
        complete_client_pixels=r['complete_client_pixels'],tier_dependent_pre_catchup_differences=differences,
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        preceding_strict_log_comparison='INCOMPLETE: pending master clocks and pre-flush SPC port clock reflect AOT/LLE batching; field/PC/master/post-flush port clock and all native video/WRAM/PCM/visual state match',
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(args.case,result['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
