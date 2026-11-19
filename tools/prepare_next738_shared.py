"""Prepare reviewed shared Wildebeest pose/color metadata, without pixel assets."""
import runpy,collections
from audit_scenes import ROOT
d=runpy.run_path(str(ROOT/'tools/audit_next731_sprites.py'));families=[r for r in d['rows']if r['family'].startswith('wildebeest')];family={'exact_pairs':list({p['snes']:p for r in families for p in r['exact_pairs']}.values())};votes={c:collections.Counter() for c in range(1,16)};poses=[]
for pair in family['exact_pairs']:
 a=d['image'](d['hydrated'][3],pair['snes'],False);b=d['image'](d['md_hydrated'][3],pair['md'][0],True)
 assert a[2:4]==b[2:4]
 for c,e in zip(a[4],b[4]):
  if c and e:votes[c][e]+=1
 poses.append(int(pair['snes'],16))
mapping=[0]+[votes[c].most_common(1)[0][0] if votes[c] else c for c in range(1,16)]
text='/* Generated original shared-frame metadata; no image or code bytes. */\nstatic const unsigned next_wildebeest_poses[] = {'+','.join(hex(p) for p in sorted(poses))+'};\nstatic const unsigned char next_wildebeest_colors[16] = {'+','.join(map(str,mapping))+'};\n'
(ROOT/'engine/generated/resources/next_scene_metadata.h').write_text(text);print('SHARED',len(poses),mapping)
