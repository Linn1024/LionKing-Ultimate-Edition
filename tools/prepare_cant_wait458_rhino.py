"""Generate reviewed rhino address/palette metadata and the combined local sprite table."""
import hashlib,json,subprocess
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait458-map';out.mkdir(exist_ok=True)
header=ROOT/'engine/generated/resources/pride_sprite_map.h'
cmd=['python',str(ROOT/'tools/pride_sprite_catalog.py'),'--header',str(header),'--out',str(out/'catalog')]
with (out/'generate.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
hashes=[hashlib.sha256(s[p:p+30]).digest() for p in (0x50b9c,0x50c1c)]
meta=ROOT/'engine/runner/tlk_cw_rhino_metadata.h';meta.write_text('/* Original native rhino palette fingerprints; no palette/artwork payload. */\nstatic const unsigned char cw_rhino_palette_hashes[2][32]={'+','.join('{'+','.join('0x%02x'%b for b in h)+'}' for h in hashes)+'};\n')
paths=[Path(__file__),header,meta,*[ROOT/'tools'/n for n in ('cw_rhino_pairs.json','cw_sprite_catalog.py','pride_sprite_catalog.py')]]
(out/'report.json').write_text(json.dumps(dict(result='PREPARED_METADATA',native_poses=13,md_images=9,gameplay_changed=False,command=cmd,scope='Original rhino animation order/bounce-prefix length, descriptor palette and graphics metadata. Native animation timing retained; extra MD idle drawing has no distinct native pose.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PREPARED_METADATA',flush=True)
