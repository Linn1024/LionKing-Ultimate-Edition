"""Verify original live shared palette, preserve sources, extend owned Graveyard HUD."""
import json,shutil,struct
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
bound(ROOT/'build/graveyard490-entry/report.json')
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
expected=[(c>>1&7)|((c>>5&7)<<3)|((c>>9&7)<<6) for c in struct.unpack_from('>16H',m,0x1d78aa)]
samples=[];originals=[]
for field in (14000,16000,18000):
    p=ROOT/f'build/md-next-levels-replay/capture-{field}/cram.bin'
    cram=struct.unpack('<64H',p.read_bytes());assert list(cram[1:16])==expected[1:16]
    samples.append(dict(field=field,visible_sprite_palette_matches=True));originals.append(p)
out=ROOT/'build/graveyard491-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard489-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard491-baseline')"))
p=ROOT/'engine/runner/tlk_wide.c';s=p.read_text();old='(pride || (s_md_level==1 && descriptor==0x3b9)) && TlkResourcesHudFramesMd(kind)';assert s.count(old)==1
s=s.replace(old,'(pride || (s_md_level==1 && descriptor==0x3b9) || (s_md_level==2 && descriptor==0x3eb)) && TlkResourcesHudFramesMd(kind)')
old='if (rd16(s_frame.ram+0x1ff9e)<=1 &&';assert s.count(old)==1;s=s.replace(old,'if (rd16(s_frame.ram+0x1ff9e)<=2 &&');p.write_text(s)
p=ROOT/'engine/runner/tlk_resources.c';s=p.read_text();assert s.count("Pride Lands and Can't Wait to Be King")==4;s=s.replace("Pride Lands and Can't Wait to Be King", "Pride Lands, Can't Wait to Be King and Elephant Graveyard");p.write_text(s)
proof=ROOT/'build/graveyard491-hud-source';proof.mkdir(exist_ok=True)
paths=[Path(__file__),*originals,ROOT/'build/graveyard490-entry/report.json']
(proof/'report.json').write_text(json.dumps(dict(result='SHARED_HUD_PALETTE_VERIFIED',samples=samples,scope='Original Graveyard live sprite palette0 matches existing prepared MD cub/HUD palette; reuse renderer and native game values with actual stage/descriptor guard. No new asset, background or behavior mapping.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('GRAVEYARD_SHARED_HUD_PREPARED',samples,flush=True)
