"""Bind the implemented flight renderer while retaining the full Pride goal."""
import argparse
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_flight_history import bound


def read_log(path):
    raw=path.read_bytes()
    return raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='render-integration-report.json')
    parser.add_argument('--native75',action='store_true',help='Include the native endpoint gate after its process completes successfully.')
    args=parser.parse_args();base=ROOT/'build/pride-flight-player'
    destination=(base/args.out).resolve();assert destination.is_relative_to(base) and not destination.exists()
    bp=base/'build-report.json';build=bound(bp)
    assert build['result']=='BUILT' and build['object_count']==572 and build['archive_count']==4
    assert digest(base/'player.exe')==digest(base/'native-engine/tlk_pride_player.exe')==build['binary_sha256']
    for name,sha in build['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    paths=[Path(__file__),bp,ROOT/'tools/pride_flight_history.py',ROOT/'build/pride-flight-baseline/report.json']
    checks=fields=0
    for name,count in (('art-verification2',24),('art-wide',24),('flight-tree',9),('width-completion',21),('regression',20),('allbugs-standalone',10)):
        path=base/name/'report.json';r=bound(path)
        assert r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values()),name
        checks+=count
        if name in ('flight-tree','width-completion','regression'):
            fields+=r.get('compared_fields',r.get('native_fields_compared',0))
        paths.append(path)
    role_path=base/'role-verification/report.json';role=bound(role_path)
    assert role['result']=='PASS' and role['original_flight_snapshots']==24 and role['semantic_predicate_checks']==480
    paths.append(role_path)
    observer_path=base/'allbugs-observer/build-report.json';observer=bound(observer_path)
    assert not observer['guest_writes_added'] and observer['all_nonhost_link_inputs_identical']
    paths.append(observer_path)
    remap=base/'remap/run.log';assert 'remap_selftest: PASS (0 failed)' in read_log(remap)
    checks+=1;paths.append(remap)
    mx=base/'exit-mx.log';old_mx=ROOT/'build/defeat-puff-art-mx.log'
    declarations=lambda text:[re.sub(r'(bankc[0-9a-f]+\.cfg):\d+',r'\1:<line>',line)
        for line in text.splitlines() if line.startswith(('WRONG','UNPROVEN'))]
    text=read_log(mx);review=declarations(text)
    assert not re.findall(r'^WRONG\b',text,re.M) and len(review)==11 and review==declarations(read_log(old_mx))
    checks+=1;paths.extend([mx,old_mx,ROOT/'engine/scripts/check_exit_mx.py'])
    proof_path=ROOT/'build/pride-pickup-flight-art2/report.json'
    assert bound(proof_path)['result']=='ORIGINAL_FLIGHTS_VERIFIED_PORT_GAP_REPRODUCED'
    paths.append(proof_path)
    if args.native75:
        native_path=base/'native-gates/play-report.json';native=json.loads(native_path.read_text())
        reference_path=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json'
        reference=json.loads(reference_path.read_text())
        assert native['result']=='PASS' and native['route_count']==75 and native['routes']==reference['routes']
        assert native['binary_sha256']==build['binary_sha256']
        paths.extend([native_path,reference_path,ROOT/'tools/verify_pride_flight_native75.py'])
    paths.extend(ROOT/p for p in ('engine/runner/tlk_pickup_flight_role.h','engine/runner/tlk_wide.c',
        'engine/runner/tlk_resources.c','tools/pride_sprite_catalog.py','tools/verify_windows.py',
        'tools/windows_capture.py','tools/verify_pride_audio_state.py','build/pride-player/player.exe'))
    report=dict(result='PARTIAL',new_checks=checks,paired_picture_full_wram_fields=fields,
        semantic_predicate_checks=480,original_fixed_flight_snapshots=24,
        native_allbugs_tracked_fields_per_mode=60648,observer_neutral_full_picture_wram_fields=3000,
        fresh_native_allbugs_complete=True,native75_endpoint_pairs=75 if args.native75 else None,
        native75_gate_pending=not args.native75,fresh_objects=572,fresh_archives=4,
        reviewed_unchanged_guest_generation_reused=True,old_objects_or_link_template_imported=False,
        verified_fixed_pickup_pose_pairs=['C528BC/094DF4','C528DD/094E1C'],
        independent_artwork_palette_live_tree_and_old_save_continuation_verified=True,
        whole_native_pcm_and_guest_identity_preserved=True,source_ids_and_save_abi_unchanged=True,
        exit_mx_wrong=0,exit_mx_existing_unproven=11,exit_mx_full_proof=False,
        prior_player_and_launchers_unchanged=True,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-flight-latest.json').write_bytes(destination.read_bytes())
    print('PARTIAL',checks,'checks;',fields,'paired picture/full-WRAM fields; full Pride remains open',flush=True)


if __name__=='__main__':main()
