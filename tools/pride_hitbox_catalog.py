"""Generate pose-address metadata for body bounds; never select ambiguous shapes.

Identical artwork alone cannot choose between different MD collision headers.
Such native poses keep their original bounds until action-specific evidence is
available. Reviewed NPC animation correspondences use their explicit metadata.
"""
import json
import struct
from pathlib import Path
from audit_scenes import ROOT, read_rom


def main():
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    catalog=json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())
    combined={int(row['snes'],16):dict(row,role=0) for group in ('exact_matches','pixel_art_variants') for row in catalog[group]}
    roles={'hyena':1,'lizard':2,'porcupine':3}
    for pair in json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']:
        native=int(pair['snes'],16)&0x3fffff
        # Keep the previously prepared shared Sun records; unreviewed other
        # NPC roles retain the catalog's original native-fallback policy.
        if pair['role']!='continue_token':combined.pop(native,None)
        if pair['role'] in roles:
            combined[native]={'md':[pair['md']],'role':roles[pair['role']]}
    # Reviewed animation correspondences, not visual-size or nearest-image guesses.
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    for a,b in json.loads((ROOT/'tools/graveyard_vulture_pairs.json').read_text())['pairs']:
        native=int(a,16)&0x3fffff;external=int(b,16)
        if struct.unpack_from('<4h',snes,native+12)!=struct.unpack_from('>4h',md,external+12):
            assert native not in combined
            combined[native]={'md':[b],'role':4}
    for pair in json.loads((ROOT/'tools/later_actor_pairs.json').read_text())['pairs']:
        if pair['role']==19:
            combined[int(pair['snes'],16)&0x3fffff]={'md':[pair['md']],'role':1}
    # Every valid Scar frame in its original bank was checked for duplicate
    # drawings with differing bounds; these reviewed mappings are unambiguous.
    for pair in json.loads((ROOT/'tools/scar_bounds_pairs.json').read_text())['pairs']:
        combined[int(pair['snes'],16)&0x3fffff]={'md':[pair['md']],'role':5}
    # Original Pride bonus-bug descriptors C586C0 / 0950D2 and their live
    # C529ED / 094F0C images. Scope selection to that owner at runtime.
    assert 0x529ed not in combined
    combined[0x529ed]={'md':['0x94f0c'],'role':6}
    for pair in json.loads((ROOT/'tools/cw_tail_bounds_pairs.json').read_text())['pairs']:
        native=int(pair['snes'],16)&0x3fffff
        assert native not in combined
        combined[native]={'md':[pair['md']],'role':7}
    # Original rhino animation correspondence already reviewed for artwork;
    # its actor-owned body contact uses these same signed rectangle headers.
    for a,b in json.loads((ROOT/'tools/cw_rhino_pairs.json').read_text())['pairs']:
        native=int(a,16)&0x3fffff
        assert native not in combined
        combined[native]={'md':[b],'role':8}
    # Hunt bug owners have explicit original descriptor/animation pairs. Keep
    # their family separate even when the same pose has an older catalog row;
    # sharing an address must not replace another family's prepared policy.
    hunt=[(int(p['snes'],16)&0x3fffff,{'md':[p['md']],'role':9})
          for p in json.loads((ROOT/'tools/bonus_actor_pairs.json').read_text())['pairs'] if p['role']==4]
    assert len(hunt)==12 and len({a for a,_ in hunt})==12
    # Original gorilla action-phase correspondences already reviewed for art.
    # Keep their bounds family distinct from every older owner of the pose.
    gorilla=[(int(p['snes'],16)&0x3fffff,{'md':[p['md']],'role':10})
             for p in json.loads((ROOT/'tools/hakuna_gorilla_pairs.json').read_text())['pairs']]
    assert len(gorilla)==55 and len({a for a,_ in gorilla})==55
    # Explicit original adult hurt phase correspondence; these drawings do
    # not have automatic visual-catalog matches. Bounds only, no point claim.
    hurt=[(int(p['snes'],16)&0x3fffff,{'md':[p['md']],'role':0})
          for p in json.loads((ROOT/'tools/adult_hurt_bounds_pairs.json').read_text())['pairs']]
    assert len(hurt)==9
    for a,row in hurt:
        if a in combined:assert combined[a]['role']==0 and combined[a]['md']==row['md']
    hurt=[(a,row)for a,row in hurt if a not in combined]
    assert len(hurt)==2
    lines=['/* Generated address correspondences only; source bounds are read from ROMs. Do not commit. */',
           'static const struct HitboxPoseMap { unsigned snes,md,role; } hitbox_map[] = {']
    ambiguous=[];count=0
    for native,row in sorted([*combined.items(),*hunt,*gorilla,*hurt],key=lambda r:(r[0],r[1]['role'])):
        candidates=[int(p,16) for p in row['md']]
        boxes={struct.unpack_from('>4h',md,p+12) for p in candidates}
        if len(boxes)!=1:
            ambiguous.append({'snes':native,'md_candidates':candidates,'reason':'Identical artwork has different original body bounds'})
            continue
        lines.append(f'{{0x{native:x},0x{candidates[0]:x},{row["role"]}}},');count+=1
    lines.append('};\n')
    # Point headers need their own ambiguity review: equal body rectangles do
    # not prove equal contact points in every matching original MD record.
    point_ambiguous=[];point_count=0
    lines.append('static const struct SimbaPointPoseMap { unsigned snes,md; } simba_point_map[] = {')
    for native,row in sorted(combined.items()):
        if row['role']!=0:continue
        candidates=[int(p,16) for p in row['md']]
        points={struct.unpack_from('>2h',md,p+20) for p in candidates}
        if len(points)!=1:
            point_ambiguous.append({'snes':native,'md_candidates':candidates});continue
        lines.append(f'{{0x{native:x},0x{candidates[0]:x}}},');point_count+=1
    lines.append('};\n')
    target=ROOT/'engine/generated/resources/pride_hitbox_map.h';content='\n'.join(lines)
    if not target.exists() or target.read_text()!=content:target.write_text(content)
    out=ROOT/'build/pride-hitbox-catalog';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,'mapped_pose_count':count,'mapped_point_count':point_count,'native_fallback_ambiguous_points':point_ambiguous,
        'native_fallback_ambiguous_poses':ambiguous},indent=2)+'\n')
    print('Body-bound correspondences:',count,'mapped;',len(ambiguous),'ambiguous poses retain native bounds',flush=True)


if __name__=='__main__':main()
