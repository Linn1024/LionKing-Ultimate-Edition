"""Observe production reset/reinitialization boundaries after ordinary warm play."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True)
    p.add_argument('--expect-residue',action='store_true');args=p.parse_args()
    base=ROOT/args.base;build_path=base/'build-report.json';build=bound(build_path);binary=base/'reset-probe.exe'
    assert digest(binary)==build['binary_sha256']
    out=base/'boundaries';out.mkdir();profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';observations=[];commands={}
    for kind in ('soft','init'):
        for mode in ('aot','lle'):
            for warm in (0,1,1211):
                name=f'{kind}-{mode}-{warm}';folder=out/name;folder.mkdir()
                command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--input',tape,'--frames',2,'--wide',256]
                if mode=='lle':command+=['--lle']
                env=os.environ.copy();env.update(TLK_RESET_PROBE=str(folder),TLK_RESET_KIND=kind,TLK_RESET_WARM=str(warm),TLK_RESET_ONLY='1')
                commands[name]=list(map(str,command))
                with (folder/'run.log').open('wb') as log:
                    r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
                assert r.returncode==0,(name,r.returncode)
                b=json.loads((folder/'boundary.json').read_text());b['mode']=mode
                b['reset_complete']=b['frame_after']==b['pc_after']==b['pending_after']==b['remainder_after']==0
                observations.append(b);print(name,b,flush=True)
    checks=dict(all_fresh_boundaries=all(row['reset_complete'] for row in observations),
        nonzero_warm_fraction_observed=any(row['warm'] and row['remainder_before'] for row in observations),
        mode_agreement=all([{k:v for k,v in row.items() if k!='mode'} for row in observations if row['kind']==kind and row['mode']=='aot']==[{k:v for k,v in row.items() if k!='mode'} for row in observations if row['kind']==kind and row['mode']=='lle'] for kind in ('soft','init')))
    reproduced=not checks['all_fresh_boundaries'] and checks['nonzero_warm_fraction_observed']
    paths=(Path(__file__),build_path,tape,ROOT/'tools/pride_reset_probe.c')
    report=dict(result='REPRODUCED' if args.expect_residue and reproduced else 'PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,
        observations=observations,commands=commands,binary_sha256=digest(binary),
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    if report['result'] not in ('PASS','REPRODUCED'):raise SystemExit(1)


if __name__=='__main__':main()
