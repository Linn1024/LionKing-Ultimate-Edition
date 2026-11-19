"""Verify the native RAM tail bank, MD tail frames and original tail action stream."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait470-tail';out.mkdir(exist_ok=True)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921609e412170f5') if False else read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
snapshot=ROOT/'build/cant-wait-native/aot/hl_wram_5000.bin';ram=snapshot.read_bytes();work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3e0000:]=ram
md={}
for p in range(0xd10fa,0xd1400,2):
    f=md_frame(m,p)
    if f:
        b=bitmap(m,f,True,with_origin=True)
        if len(b)==5:md.setdefault(b,[]).append(p)
pairs=[]
for p in range(0x3ce90,0x3d1c0):
    if work[p]>127:continue
    f=snes_frame(work,p)
    if not f:continue
    b=bitmap(work,f,False,with_origin=True)
    if b in md:pairs.append(dict(native_pose=hex(p|0xc00000),md_poses=[hex(q) for q in md[b]],origin=b[:2],size=b[2:4]))
assert len(pairs)>=8
# Both original stream initializers belong to the rhino-tail action, with the
# tail's world anchor behind/above the separately owned rhino head.
assert s[0x2eb1c:0x2eb1f]==bytes.fromhex('a9c16c') and m[0x19cf54:0x19cf5a]==bytes.fromhex('41f9000b8d98')
palettes=ROOT/'build/cant-wait-display/aot/fields.bin';raw=palettes.read_bytes();record=struct.Struct('<276I');colors={}
for v in record.iter_unpack(raw[8:]):
    data=struct.pack('<15H',*v[20+128+16+1:20+128+32]);colors[data]=colors.get(data,0)+1
palette_sources=[dict(count=count,offset=hex(s.find(data)),sha256=hashlib.sha256(data).hexdigest()) for data,count in sorted(colors.items(),key=lambda p:-p[1])]
paths=[Path(__file__),snapshot,palettes]
(out/'report.json').write_text(json.dumps(dict(result='SHARED_TAIL_ART',pairs=pairs,palette_sources=palette_sources,descriptor='0xc58c08',action='0xc2ead2',md_descriptor='0xb8d8a',md_action='0x19cf24',scope='Actual full7E/7F bank images and exact anchored/indexed MD counterparts. Native tail action/MD counterpart initialize matching tail streams; large giraffe/rhino bodies are foreground scenery. No runtime/animation changes.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('tail frames',len(pairs),pairs,'palettes',palette_sources,flush=True)
