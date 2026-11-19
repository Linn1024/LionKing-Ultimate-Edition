"""Settle in-flight source edits and bind the final caption executable."""
import json
import argparse
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',default='final-build2.json');parser.add_argument('--log',default='finalize2.log')
    args=parser.parse_args()
    base=ROOT/'build/pride-title-work';initial=base/'commands.json';report=json.loads(initial.read_text())
    with (base/args.log).open('wb') as log:
        subprocess.run(report['build'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    paths=[ROOT/name for name in report['source_sha256']]
    paths += [Path(__file__),initial,base/'player/native-engine/tlk_pride_player_core-sources/game/tlk_resources.c']
    exe=base/'player/native-engine/tlk_pride_player.exe'
    result=dict(result='BUILT',binary_sha256=digest(exe),finalize=report['build'],
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={args.log:digest(base/args.log)})
    dest=base/args.report;assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
    print('Final caption candidate',result['binary_sha256'],flush=True)


if __name__=='__main__':main()
