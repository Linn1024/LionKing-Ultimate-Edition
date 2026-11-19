"""Bind the immediate original collision/rebound cause, keeping lifecycle open."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    path=ROOT/'build/pride-ground-gap/audit2.json';r=bound(path)
    assert r['result']=='PARTIAL' and r['immediate_trigger_proven'] and all(r['checks'].values())
    original=ROOT/'build/pride-ground-gap/md/report.json';md=bound(original);assert md['result']=='CAPTURED'
    report=dict(result='PARTIAL',check_count=len(r['checks']),immediate_original_contact_rebound_trigger_proven=True,
        first_remaining_controller_update_gap=dict(matched_updates=686,native_field=1631,md_field=2015),
        native_implementation_changed=False,md_movement_capability_enabled=False,full_first_level_fidelity_complete=False,
        next_work=r['next_work'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),path,original)})
    (ROOT/'build/pride-ground-gap-latest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL',report['check_count'],'checks; immediate trigger verified, enemy lifecycle remains open',flush=True)


if __name__=='__main__':main()
