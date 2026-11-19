"""Summarize actual DSP-cadence ownership without claiming unseen coverage."""
from collections import Counter
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player/dsp-owner-sample-audit'
    rp=base/'report.json';report=bound(rp);assert all(report['checks'].values())
    chain=ROOT/'build/pride-lizard-launch-work/spc-owner-chain-report.json'
    assert bound(chain)['result']=='OBSERVED_NATIVE_BOUNCE_OWNERSHIP_CHAIN_VERIFIED'
    results={}
    for name in ('native','bounce'):
        with (base/name/'samples.csv').open() as stream:rows=list(csv.DictReader(stream))
        assert rows and all(r['noise']==r['echo']=='0' and r['patch']=='62' for r in rows)
        for r in rows:
            assert int(r['owner'])<22
            assert all(int(r['program_start'],16)<=int(r[key],16)<int(r['program_end'],16)
                for key in ('base','saved_base','root_base'))
        audible=[r for r in rows if (int(r['volume_l']) or int(r['volume_r']))
            and (int(r['master_l']) or int(r['master_r'])) and r['mute']=='0']
        results[name]=dict(samples=len(rows),audible_samples=len(audible),
            software_flags=dict(Counter(r['flags'] for r in rows)),
            all_samples_owned_by_program17=True,
            banks=sorted({(r['program_start'],r['program_end']) for r in rows}))
    assert results['native']['samples']==results['native']['audible_samples']==76372
    assert results['bounce']['samples']==76299 and results['bounce']['audible_samples']==0
    paths=[Path(__file__),rp,chain]
    result=dict(result='OBSERVED_SAMPLE_CADENCE_OWNERSHIP_VERIFIED',profiles=results,
        all_unobserved_states_or_semantic_callers_proven=False,
        original_program17_has_other_native_callers=True,
        fixed_channel_or_active_software_flag_filters_are_insufficient=True,
        production_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=ROOT/'build/pride-lizard-launch-work/dsp-owner-sample-summary.json';assert not destination.exists()
    destination.write_text(json.dumps(result,indent=2)+'\n');print(result['result'],results,flush=True)


if __name__=='__main__':main()
