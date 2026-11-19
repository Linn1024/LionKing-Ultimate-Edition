"""Bind the verified ledge-audio candidate without claiming full Pride fidelity."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_ledge_history import bound


def main():
    base=ROOT/'build/pride-ledge-work/player';destination=base/'ledge-integration-report.json'
    assert not destination.exists(),'Preserve successful summaries'
    bp=base/'build-report.json';build=bound(bp);assert digest(base/'player.exe')==build['binary_sha256']
    expected={'ledge-audio':62,'ledge-saves':120,'ledge-pause2':8,'ledge-restart2':12,
        'ledge-changed-source':20,'previous-native-save':10,'regression':20,'width-completion':21,
        'ledge-route':19,'allbugs-standalone':10}
    paths=[Path(__file__),bp,ROOT/'tools/pride_ledge_history.py'];count=0
    for folder,number in expected.items():
        path=base/folder/'report.json';report=bound(path)
        assert report['result']=='PASS' and len(report['checks'])==number and all(report['checks'].values()),path
        count+=number;paths.append(path)
    gate_path=base/'native-gates/play-report.json';gate=json.loads(gate_path.read_text())
    reference_path=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json';reference=json.loads(reference_path.read_text())
    assert gate['result']=='PASS' and gate['route_count']==75 and gate['binary_sha256']==build['binary_sha256']
    assert gate['routes']==reference['routes']
    paths += [gate_path,reference_path]
    for name,result in (('build/pride-ledge-work/component/report.json','PASS'),
        ('build/pride-ledge-tags/report.json','ORIGINAL_LEDGE_TAG_BRANCHES_MATCH'),
        ('build/pride-ledge-native-stream/report.json','NATIVE_SHARED_LEDGE_STREAM_HAS_NO_SOUND_COMMANDS'),
        ('build/pride-ledge-driver-parameter/report.json','OBSERVED_FM94_PARAMETERS_PCM_IDENTICAL'),
        ('build/pride-ledge-stream-pair/report.json','ORIGINAL_LEDGE_STREAM_PROTOCOLS_CORRESPOND')):
        path=ROOT/name;assert bound(path)['result']==result;paths.append(path)
    def static_rows(path):
        data=path.read_bytes();text=data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
        return [re.sub(r'(bank\w+\.cfg):\d+',r'\1:LINE',row) for row in text.splitlines() if row.startswith(('WRONG','UNPROVEN'))]
    current=ROOT/'build/pride-ledge-work/exit-mx.log';previous=ROOT/'build/pride-arrival-work/exit-mx-reviewed.log'
    rows=static_rows(current);assert rows==static_rows(previous) and len(rows)==11 and not any(r.startswith('WRONG') for r in rows)
    paths += [current,previous,ROOT/'build/pride-ledge-work/remap.log',ROOT/'build/pride-ledge-work/python-tests.log']
    report=dict(result='PARTIAL',checks=count,binary_sha256=build['binary_sha256'],
        ordinary_comparison_fields=64600,cold_prefix_comparison_fields=25576,cold_remaining_comparison_fields=56848,
        changed_source_comparison_fields=12092,previous_build_prefix_and_continuation_fields=7530,
        total_full_picture_wram_field_comparisons=166646,
        matching_cold_process_mode_combinations=24,changed_source_process_combinations=4,previous_build_load_modes=2,
        native75_endpoint_pairs=75,native_allbugs_tracked_fields_per_mode=60648,
        independent_original_tag_branch_comparisons=512,component_word_tags_per_direction=65536,
        static_wrong=0,static_unproven=11,complete_static_proof=False,
        preview_promoted=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    assert count==302
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL302;166646 repeated full-field comparisons;75 native pairs; full Pride remains open',flush=True)


if __name__=='__main__':main()
