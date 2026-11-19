"""Aggregate the bounded arrival-audio candidate evidence without claiming full fidelity."""
import argparse
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arrival_history import bound


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native75',action='store_true')
    parser.add_argument('--out',default='arrival-integration-report.json')
    args=parser.parse_args();base=ROOT/'build/pride-arrival-work/player'
    output=base/args.out;assert not output.exists(),'Preserve existing integration reports'
    paths=[base/'build-report.json',base/'arrival-audio/report.json',base/'arrival-saves/report.json',
           base/'arrival-pause/report.json',base/'regression/report.json',base/'width-completion2/report.json',
           ROOT/'build/pride-arrival-tail/report.json']
    build=bound(paths[0]);checks=0
    assert digest(base/'player.exe')==build['binary_sha256']
    for path in paths[1:]:
        report=bound(path);assert report['result']=='PASS',(path,report['result'])
        assert all(report.get('checks',{}).values()),path
        checks+=len(report.get('checks',{}))
    current_log=ROOT/'build/pride-arrival-work/exit-mx-reviewed.log'
    previous_log=ROOT/'build/pride-flight-player/exit-mx.log'
    def static_rows(path):
        data=path.read_bytes()
        text=data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
        return [re.sub(r'(bank\w+\.cfg):\d+',r'\1:LINE',line) for line in text.splitlines()
                if line.startswith(('WRONG','UNPROVEN'))]
    static=static_rows(current_log)
    assert static==static_rows(previous_log)
    assert not any(row.startswith('WRONG') for row in static) and len(static)==11
    paths += [current_log,previous_log]
    if args.native75:
        path=base/'native-gates/play-report.json';report=json.loads(path.read_text())
        assert report['result']=='PASS' and report['route_count']==75
        assert report['binary_sha256']==build['binary_sha256']
        baseline=json.loads((ROOT/'build/pride-reset/fixed4/native/gates/play-report.json').read_text())
        assert report['routes']==baseline['routes']
        paths+=[path,ROOT/'build/pride-reset/fixed4/native/gates/play-report.json']
    paths+=[Path(__file__),ROOT/'tools/pride_arrival_history.py']
    result=dict(result='PARTIAL',checks=checks,binary_sha256=build['binary_sha256'],
        scope='Independent Pride Lands HUD pickup-arrival audio candidate; launcher unchanged',
        isolated_profiles=5,isolated_profile_fields_each=2000,paired_picture_full_wram_fields=28500,
        cold_process_mode_combinations=20,completion_fields=4500,
        completion_route_exercises_arrival=False,separate_pickup_route_exercises_two_arrivals=True,
        native_endpoint_pairs=75 if args.native75 else 0,
        static_exit_mx=dict(raw_exit=1,wrong=0,unproven=11,complete_static_proof=False),
        full_first_level_fidelity_complete=False,preview_promoted=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,'checks; native endpoint pairs',result['native_endpoint_pairs'],flush=True)


if __name__=='__main__':main()
