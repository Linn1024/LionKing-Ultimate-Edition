"""Verify stable resource indices and popup parents in both maintained graphs."""
import json
from pathlib import Path
import re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def nodes(path):
    source=path.read_text()
    source=source[source.index('static const TlkResourceNode nodes[]'):source.index('enum { COUNT')]
    return [(name,int(parent)) for name,parent in re.findall(r'^\s*\{"([^"]+)", "[^"]*", (-?\d+),',source,re.M)]


def main():
    out=ROOT/'build/pride-popup-work/schema';out.mkdir()
    prefix='graphics.sprites.effects.pickup_arrival'
    paths=[];checks={};observations={}
    for graph,before,after in (
        ('normal','build/pride-popup-baseline/sources/engine/runner/tlk_resources.c','engine/runner/tlk_resources.c'),
        ('standalone','build/pride-scene-template-work/player/native-engine/tlk_pride_player_core-sources/game/tlk_resources.c',
         'build/pride-popup-work/player/native-engine/tlk_pride_player_core-sources/game/tlk_resources.c')):
        a,b=ROOT/before,ROOT/after;old,new=nodes(a),nodes(b);paths += [a,b]
        checks[graph+'/all_existing_indices_parents_preserved']=new[:len(old)]==old
        checks[graph+'/four_new_nodes_appended']=len(new)==len(old)+4
        branch=next(i for i,(name,parent) in enumerate(new) if name==prefix)
        for leaf in ('frames','palette','position'):
            entry=next((i,parent) for i,(name,parent) in enumerate(new) if name==prefix+'.'+leaf)
            checks[graph+'/'+leaf+'_parent']=entry[1]==branch
        checks[graph+'/acyclic_parent_before_child']=all(parent<i for i,(name,parent) in enumerate(new))
        observations[graph]=dict(previous_count=len(old),current_count=len(new),popup_branch=branch)
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),*paths]})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'resource schema checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
