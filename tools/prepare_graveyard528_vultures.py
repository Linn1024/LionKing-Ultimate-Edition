"""Promote original vulture phase metadata, validating streams and default owners."""
import json,subprocess
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard526-vulture-pairs/report.json';r=bound(reference);assert not r['missing']
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
pairs=r['pairs']+[['0xc3efbd','0xe72ee']]
# The takeoff stream's following record, omitted by the family-range inventory.
assert s[0x281e9:0x281ed]==bytes.fromhex('02bdefc3') and m[0xd15f2:0xd15f6]==bytes.fromhex('020e72ee')
# Fixed idle frame and the two full initial idle loops, before their FF loops.
assert s[0x2811c:0x28124]==bytes.fromhex('0560fac3632dfac3')
assert m[0xd159a:0xd15a2]==bytes.fromhex('050e8206630e81ce')
descriptors=[0xc58cca,0xc58cd8,0xc58ce6,0xc58cf2,0xc58d00]
for p in descriptors:assert s[(p&0x3fffff)+3:(p&0x3fffff)+8]==bytes.fromhex('3a00022dfa')
for p in (0xd13f6,0xd1406,0xd1416):assert (int.from_bytes(m[p+4:p+6],'big')>>13&3)==3
spec=ROOT/'tools/graveyard_vulture_pairs.json';spec.write_text(json.dumps(dict(scope='Original vulture animation-family phases, native timing retained. 45 reviewed frame records plus the shared takeoff terminal frame. Native/MD art and some phase timing differ; direct native ownership is required. No pixels or palettes.',pairs=sorted(pairs,key=lambda x:int(x[0],16)),streams=r['streams'],native_descriptors=[hex(p) for p in descriptors]),indent=2)+'\n')
meta=ROOT/'engine/runner/tlk_graveyard_enemy_metadata.h';meta.write_text('/* Original Graveyard actor descriptors; address metadata only. */\nstatic const unsigned graveyard_vulture_descriptors[]={'+','.join(hex(p) for p in descriptors)+'};\n')
header=ROOT/'engine/generated/resources/pride_sprite_map.h';out=ROOT/'build/graveyard528-vulture-map';out.mkdir(exist_ok=True)
cmd=['python',str(ROOT/'tools/pride_sprite_catalog.py'),'--header',str(header),'--out',str(out/'catalog')]
with (out/'generate.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
paths=[Path(__file__),reference,spec,meta,header,ROOT/'tools/graveyard_sprite_catalog.py',ROOT/'tools/pride_sprite_catalog.py']
(out/'report.json').write_text(json.dumps(dict(result='PREPARED_METADATA',native_poses=len(pairs),md_images=len({p[1] for p in pairs}),command=cmd,scope='All original phase records and the actual idle/takeoff records. Existing prepared sprite format; native timing/gameplay retained. Native palette5 is prepared from original table2F727; MD colors from existing Graveyard scene bank3.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('VULTURE_METADATA',len(pairs),flush=True)
