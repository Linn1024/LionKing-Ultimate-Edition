"""Extend a bound repair index with completed mixture and public preservation."""
import argparse
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_scene_template_history import bound


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-report',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    parent=args.base_report.resolve();report=bound(parent)
    assert report['result']=='PARTIAL' and report['allbugs_complete']
    base=ROOT/'build/pride-scene-template-work/player'
    paths=[base/'width-completion/report.json',base/'completion-baseline/report.json']
    result=dict(report);result['reports']=dict(report['reports'])
    for name,path in zip(('supported_mixture_completion','preceding_public_completion'),paths):
        child=bound(path);assert child['result']=='PASS' and all(child['checks'].values())
        result['checks']+=len(child['checks'])
        result['reports'][name]=dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),checks=len(child['checks']))
    result['source_sha256']={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),parent,*paths]}
    result['parent_integration']=parent.relative_to(ROOT).as_posix()
    target=args.out.resolve();assert not target.exists()
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],result['checks'],'native75 complete',result['native75_complete'],flush=True)


if __name__=='__main__':main()
