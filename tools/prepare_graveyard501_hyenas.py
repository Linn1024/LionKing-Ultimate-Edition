"""Preserve sources and prove existing hyena art/scene-specific prepared colors."""
import json,shutil,struct
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
bound(ROOT/'build/graveyard494-hud/report.json')
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
offset=int.from_bytes(m[0x1cfdb4+2*48+44:0x1cfdb4+2*48+48],'big')
expected=[(c>>1&7)|((c>>5&7)<<3)|((c>>9&7)<<6) for c in struct.unpack_from('>64H',m,offset)]
paths=[Path(__file__),ROOT/'tools/pride_npc_pairs.json',ROOT/'build/graveyard499-actors/report.json'];samples=[]
for field in (14000,16000,18000):
    p=ROOT/f'build/md-next-levels-replay/capture-{field}/cram.bin';cram=struct.unpack('<64H',p.read_bytes());assert list(cram[49:64])==expected[49:64];paths.append(p);samples.append(field)
pairs=json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs']
observed=[]
for native in (0xc2b530,0xc2b75e):
    pair=next(p for p in pairs if int(p['snes'],16)==native);assert pair['role']=='hyena' and pair['native_palette']==6 and pair['md_palette']==3;observed.append(pair)
out=ROOT/'build/graveyard501-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/runner/tlk_md_assets.c','engine/runner/tlk_md_assets.h','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard491-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard501-baseline')"))
out=ROOT/'build/graveyard501-hyena-source';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='EXISTING_HYENA_RESOURCES_VERIFIED',palette_original_offset=hex(offset),original_palette_samples=samples,existing_pairs=observed,native_descriptor='0xc58c74',scope='Opening actors are hyenas, not vultures. Existing reviewed Pride mappings apply; original Graveyard palette3 differs from Pride and matches its own prepared scene table. Research495/496 incorrectly queried vulture counterparts; no runtime mappings were made from nearest masks.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('HYENA_REUSE_PROVED',hex(offset),flush=True)
