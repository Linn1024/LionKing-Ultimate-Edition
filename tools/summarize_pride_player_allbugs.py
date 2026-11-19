"""Bind the standalone native All Bugs gate without replacing historical indexes."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-player'
    prior_path=base/'integration-report.json'
    prior=bound(prior_path)
    assert prior['result']=='PARTIAL' and prior['new_checks']==162
    build_path=base/'build-report.json';build=bound(build_path)
    observer_path=base/'allbugs-observer/build-report.json';observer=bound(observer_path)
    assert observer['result']=='BUILT' and observer['all_nonhost_link_inputs_identical']
    assert observer['production_binary_unchanged'] and not observer['guest_writes_added']
    assert digest(base/'player.exe')==digest(base/'native-engine/tlk_pride_player.exe')==build['binary_sha256']
    assert digest(base/'allbugs-observer/player.exe')==observer['binary_sha256']
    for name,sha in observer['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    gate_path=base/'allbugs-standalone/report.json';gate=bound(gate_path)
    assert gate['result']=='PASS' and len(gate['checks'])==10 and all(gate['checks'].values())
    assert gate['compared_fields']==60648
    research_path=ROOT/'build/pride-ambiguous-caller2/report.json';research=bound(research_path)
    assert research['result']=='BOUNDED_CALLBACK_SELECTION_PASS'
    assert research['original_cpu_cases']==196608 and research['cub_age_can_select_adult_callback']
    assert research['production_mappings_unchanged'] and not research['ordinary_pride_reachability_proven']
    paths=[Path(__file__),prior_path,build_path,observer_path,gate_path,research_path]
    report=dict(result='PARTIAL',new_checks=172,compared_fields=113266,
        new_allbugs_checks=10,native_allbugs_tracked_fields_per_mode=60648,
        observer_neutral_full_picture_wram_fields=3000,native_endpoint_route_pairs=75,
        fresh_allbugs_gate_complete=True,original_indirect_callback_cpu_cases=196608,
        ordinary_pride_indirect_callback_scope_closed=False,production_binary_unchanged=True,
        release_and_legacy_save_migration_complete=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=base/'allbugs-integration-report.json'
    assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    latest=ROOT/'build/pride-player-allbugs-latest.json'
    assert not latest.exists()
    latest.write_bytes(destination.read_bytes())
    print('PARTIAL172; All Bugs PASS10 /60648 tracked fields per mode; production unchanged',flush=True)


if __name__=='__main__':main()
