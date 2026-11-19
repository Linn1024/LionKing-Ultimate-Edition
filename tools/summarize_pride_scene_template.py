"""Bind completed reload-repair gates; keep the full first-level goal open."""
import argparse
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_scene_template_history import bound


def log_text(path):
    data=path.read_bytes()
    return data.decode('utf-16') if data.startswith((b'\xff\xfe',b'\xfe\xff')) else data.decode('utf-8-sig')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native75',action='store_true');parser.add_argument('--allbugs',action='store_true')
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    base=ROOT/'build/pride-scene-template-work/player'
    bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==digest(base/'native-engine/tlk_pride_player.exe')==build['binary_sha256']
    reports={
        'native_fallback_and_old_save':base/'fallback/report.json',
        'owned_mixed_and_old_save':base/'owned-regression/report.json',
        'retained_capsules':ROOT/'build/pride-bounce-owner-work/player/fallback-probe3/preserve/report.json',
    }
    children={};checks=0
    for name,path in reports.items():
        report=bound(path);assert report['result']=='PASS' and all(report['checks'].values())
        children[name]=dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),checks=len(report['checks']))
        checks+=len(report['checks'])
    assert checks==60
    if args.allbugs:
        path=base/'allbugs-standalone/report.json';report=bound(path)
        assert report['result']=='PASS' and all(report['checks'].values()) and report['compared_fields']==60648
        reports['allbugs']=path;children['allbugs']=dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),checks=len(report['checks']))
        checks+=len(report['checks'])
    if args.native75:
        path=base/'native-gates/play-report.json';report=json.loads(path.read_text())
        previous=json.loads((ROOT/'build/pride-bounce-owner-work/player/native-gates/play-report.json').read_text())
        assert report['result']=='PASS' and report['route_count']==75 and report['binary_sha256']==build['binary_sha256']
        assert report['routes']==previous['routes']
        reports['native75']=path;children['native75']=dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),route_pairs=75)
        checks+=75
    work=base.parent;tests=work/'python-tests.log';remap=work/'remap.log';mx=work/'exit-mx.log'
    assert '23 passed, 4 skipped' in log_text(tests)
    assert 'PASS (0 failed)' in log_text(remap)
    lines=log_text(mx).splitlines();prior=log_text(ROOT/'build/pride-bounce-owner-work/exit-mx.log').splitlines()
    assert not any(line.startswith('WRONG') for line in lines)
    assert [line for line in lines if line.startswith('UNPROVEN')]==[line for line in prior if line.startswith('UNPROVEN')]
    public=ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    assert digest(public)=='f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    paths=[Path(__file__),bp,*reports.values(),tests,remap,mx,ROOT/'engine/runner/pride/pride_scene_template.h',ROOT/'build/pride-scene-template-baseline/report.json']
    report=dict(result='PARTIAL',checks=checks,reports=children,binary_sha256=build['binary_sha256'],
        fresh_objects=build['object_count'],fresh_archives=build['archive_count'],
        python_tests=dict(passed=23,skipped=4),remap_failed=0,exit_mx_wrong=0,
        exit_mx_same_unproven=sum(line.startswith('UNPROVEN') for line in lines),
        allbugs_complete=args.allbugs,native75_complete=args.native75,
        public_preview_changed=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    target=args.out.resolve();assert not target.exists(),'Preserve prior integration evidence'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,'checks; All Bugs',args.allbugs,'native75',args.native75,flush=True)


if __name__=='__main__':main()
