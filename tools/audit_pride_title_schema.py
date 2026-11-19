"""Verify caption resource parents and preserve every pre-existing node index."""
import json
from pathlib import Path
from audit_scenes import ROOT
from audit_pride_popup_schema import nodes
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-title-work/schema';out.mkdir()
    checks={};observations={};paths=[]
    for graph,old,new in (
        ('normal','build/pride-title-baseline/sources/engine/runner/tlk_resources.c','engine/runner/tlk_resources.c'),
        ('standalone','build/pride-popup-work/player/native-engine/tlk_pride_player_core-sources/game/tlk_resources.c',
         'build/pride-title-work/player/native-engine/tlk_pride_player_core-sources/game/tlk_resources.c')):
        a,b=ROOT/old,ROOT/new;before,after=nodes(a),nodes(b);paths += [a,b]
        checks[graph+'/existing_indices_parents_preserved']=after[:len(before)]==before
        checks[graph+'/six_nodes_appended']=len(after)==len(before)+6
        branch=next(i for i,(name,parent) in enumerate(after) if name=='graphics.titles.pride_lands')
        checks[graph+'/caption_group_parent']=after[after[branch][1]][0]=='graphics.titles'
        for leaf in ('frames','palette','position','duration'):
            parent=next(parent for name,parent in after if name=='graphics.titles.pride_lands.'+leaf)
            checks[graph+'/'+leaf+'_parent']=parent==branch
        observations[graph]=dict(previous_count=len(before),current_count=len(after),caption_branch=branch)
    paths += [Path(__file__),ROOT/'tools/audit_pride_popup_schema.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'caption schema checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
