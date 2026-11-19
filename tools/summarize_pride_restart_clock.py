"""Bind restart audio repair and ordinary native compatibility evidence."""
import argparse
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

BASE=ROOT/'build/pride-restart-clock'


def bound(path):
    report=json.loads(path.read_text())
    for name,sha in report.get('source_sha256',{}).items():assert digest(ROOT/name)==sha,(path,name)
    for name,sha in report.get('artifacts_sha256',{}).items():assert digest(path.parent/name)==sha,(path,name)
    return report


def check_build(path,prefix):
    report=bound(path)
    for name,sha in report['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for host,run in report['runs'].items():
        assert digest(path.parent/f'{prefix}-{host}.exe')==run['binary_sha256']
        for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pending-native',action='store_true',help='Publish a scoped index while native gates run')
    args=parser.parse_args();paths=[]
    build_path=BASE/'build-report.json';build=check_build(build_path,'restart');paths.append(build_path)
    native_build_path=BASE/'native/build-report.json';native_build=check_build(native_build_path,'native');paths.append(native_build_path)
    windows={}
    for name in ('native-aot','md-lle'):
        path=BASE/f'final/windows/{name}/report.json';r=bound(path);paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values())
        assert r['binary_sha256']==build['runs']['sdl']['binary_sha256']
        windows[name]=len(r['checks'])
    for n in (0,1):
        path=BASE/f'final/owned-saves/{n}/report.json';r=bound(path);paths.append(path)
        assert r['result']=='PASS' and all(r['checks'].values())
        assert r['binary_sha256']==build['runs']['probe']['binary_sha256']
    sync_path=BASE/'sync-trace/report.json';sync=bound(sync_path);paths.append(sync_path)
    assert sync['result']=='PASS' and not sync['differences']
    snapshot_bytes=0
    for field in range(2698,2703):
        for point in ('before','after'):
            for suffix in ('guest','audio'):
                name=f'sync-{field}-{point}.{suffix}'
                a=(BASE/'sync-trace/baseline'/name).read_bytes();b=(BASE/'sync-trace/before'/name).read_bytes()
                assert a==b,name;snapshot_bytes+=len(a)
    old_sync_path=ROOT/'build/pride-restart/sync-trace/report.json';old=bound(old_sync_path);paths.append(old_sync_path)
    assert old['differences']==301 and old['first'][0]['field']=='2700'
    early_path=BASE/'native/early-state/report.json';early=bound(early_path);paths.append(early_path)
    assert early['result']=='PASS' and all(early['checks'].values()) and early['saved_remainder']==11975040
    layout_path=BASE/'native/early-state/layout-report.json';layout=bound(layout_path);paths.append(layout_path)
    assert layout['result']=='PASS' and not layout['port_time_valid'] and layout['port_clock']==14244
    assert digest(layout_path.parent/'layout.exe')==layout['binary_sha256']
    native_window_path=BASE/'native/windows/report.json'
    native_windows_ready=native_window_path.exists()
    if native_windows_ready:
        r=bound(native_window_path);paths.append(native_window_path)
        assert r['result']=='PASS' and all(r['checks'].values())
        assert r['after_binary_sha256']==native_build['runs']['sdl']['binary_sha256']
    elif not args.pending_native:raise AssertionError('Native window comparison still pending')
    gates_ready=False;native_reports={}
    for filename in ('play-report.json','allbugs-report.json'):
        path=BASE/'native/gates'/filename;r=json.loads(path.read_text())
        native_reports[filename]=r
    if all(r['result']=='PASS' for r in native_reports.values()):
        gates_ready=True
        for filename,r in native_reports.items():
            path=BASE/'native/gates'/filename;paths.append(path)
            assert r['binary_sha256']==native_build['runs']['headless']['binary_sha256']
            assert r['verifier_sha256']==digest(ROOT/'tools/verify_native_routes.py')
            previous_path=ROOT/'build/pride-checkpoint-player/native3'/filename
            previous=json.loads(previous_path.read_text());paths.append(previous_path)
            assert r['routes']==previous['routes'],filename
        assert native_reports['play-report.json']['route_count']==75
        assert native_reports['allbugs-report.json']['allbugs_tracked_ram_equal_every_frame']
        a=BASE/'native/gates/allbugs-aot.ram';b=BASE/'native/gates/allbugs-lle.ram'
        old=ROOT/'build/pride-checkpoint-player/native3/allbugs-aot.ram'
        assert a.read_bytes()==b.read_bytes()==old.read_bytes()
        paths.extend((a,b,old))
    elif not args.pending_native:raise AssertionError('Native route gates still pending')
    tools=('probe_pride_restart_clock.py','verify_pride_restart_clock_owned.py','verify_native_routes.py',
        'pride_restart_sync_trace.c','pride_restart_audio_trace.c','trace_pride_restart_clock_sync.py')
    paths.extend(ROOT/'tools'/name for name in tools)
    paths.extend(sorted((ROOT/'engine/build/playtapes').glob('*.tape')))
    paths.extend((ROOT/'engine/tapes/allbugsF.read.tape',ROOT/'engine/tapes/6987M.read.tape',
        ROOT/'Lion King, The (USA).sfc',Path(__file__)))
    result=dict(result='PARTIAL' if gates_ready and native_windows_ready else 'NATIVE_GATES_PENDING',scope=__doc__,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        windows_checks=windows,owned_cross_mode_saves=2,consumer_records_equal=3000,
        guest_audio_snapshot_pairs_equal=20,snapshot_bytes_compared=snapshot_bytes,
        saved_early_relative_remainder=early['saved_remainder'],native_early_resume_modes=2,
        native_windows_verified=native_windows_ready,native_routes_verified=gates_ready,
        native_route_count=75 if gates_ready else None,allbugs_fields=60648 if gates_ready else None,
        selected_restart_audio_fixed=True,actual_live_level_menu_verified=False,practice_f9_restart_verified=False,
        hardware_reset_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-restart-clock-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],'restart matrices',sum(windows.values()),'checks; consumer3000 exact; snapshots',snapshot_bytes,flush=True)


if __name__=='__main__':main()
