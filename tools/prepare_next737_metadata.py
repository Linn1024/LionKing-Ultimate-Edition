"""Freeze reviewed frame links/color-index maps, never extracted image bytes."""
import runpy,json,collections
from audit_scenes import ROOT
d=runpy.run_path(str(ROOT/'tools/audit_next731_sprites.py'));reports=d['rows'];image=d['image'];spec=[]
roles={'stampede-cub':(11,3,2,0),'rocks':(12,3,1,1)}
for family in reports:
 name=family['family']
 if name not in roles:continue
 role,level,bank,md_bank=roles[name];s=d['hydrated'][level];m=d['md_hydrated'][level]
 pairs=family['silhouette_pairs']
 if name=='exile-running-lizard':
  ns=sorted({r['pose'] for r in d['native'] if r['descriptor']==family['native_descriptor']});ms=sorted({r['pose'] for r in d['external'] if r['descriptor']==family['md_descriptor']});assert len(ns)==len(ms)==7
  pairs=[dict(snes=p,md=[q]) for p,q in zip(ns,ms)]
 for pair in pairs:
  p=pair['snes'];q=pair['md'][0];a=image(s,p,False);b=image(m,q,True)
  if not a or not b:continue
  # Per-pose color votes preserve different tongue/body index assignments.
  def mapping(source,target):
   votes={c:collections.Counter() for c in range(1,16)}
   for y in range(min(source[3],target[3])):
    for x in range(min(source[2],target[2])):
     c=source[4][y*source[2]+x];e=target[4][y*target[2]+x]
     if c and e:votes[c][e]+=1
   return [0]+[votes[c].most_common(1)[0][0] if votes[c] else c for c in range(1,16)]
  spec.append(dict(snes=p,md=q,role=role,native_palette=bank,md_palette=md_bank,native_to_md=mapping(a,b),md_to_native=mapping(b,a),basis='exact opacity silhouette; differing indexed colors' if name!='exile-running-lizard' else 'seven original ordered running-animation phases; drawings visually reviewed'))
(ROOT/'tools/next_scene_pairs.json').write_text(json.dumps(dict(scope='Stampede cub/rocks and Exile lizard/chameleon original frame correspondences. Artwork only, gameplay independent. Unknown poses retain native art.',pairs=spec),indent=2)+'\n');print('REVIEWED links',len(spec))
