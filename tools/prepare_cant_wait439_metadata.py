"""Write reviewed address/fingerprint metadata, never artwork or palette payloads."""
import hashlib,json,struct
from audit_scenes import ROOT,read_rom
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
reference=ROOT/'build/cant-wait437-monkeys/report.json';ref=bound(reference)
rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
poses=[int(p['native_pose'],16) for p in ref['pairs']];assert len(poses)==29
# The bounded old scan started43E00. Its earlier valid intro pose shares the
# exact original MD drawing and the same actor/palette ownership guards.
from pride_sprite_catalog import snes_frame,md_frame,bitmap
md_rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
intro_ref=bound(ROOT/'build/cant-wait435-animals/report.json')
intro_ram=(ROOT/intro_ref['native_bank_snapshot']).read_bytes()
intro_work=bytearray(rom);intro_work.extend(bytes(0x400000-len(intro_work)))
intro_work[0x3f0000:]=intro_ram[0x10000:]
assert bitmap(intro_work,snes_frame(intro_work,0x43dcc),False,with_origin=True)==bitmap(md_rom,md_frame(md_rom,0xcec52),True,with_origin=True)
poses=[0xc43dcc]+poses;assert len(poses)==30

descriptors=sorted({int(p['descriptor'],16) for p in ref['live']})
palettes=ROOT/'build/cant-wait-display/aot/fields.bin';raw=palettes.read_bytes();record=struct.Struct('<276I')
# Initial OBJ colors and later full-scene palette use different CGRAM destinations.
sources=((0x50bbc,0x602f7),(0x50bdc,0x60317));fingerprints=[]
for bank,offsets in zip((2,3),sources):
    colors=[rom[p:p+30] for p in offsets];seen=[False,False]
    for v in record.iter_unpack(raw[8:]):
        live=struct.pack('<15H',*v[20+128+bank*16+1:20+128+bank*16+16])
        for n,c in enumerate(colors):seen[n]|=live==c
    assert all(seen),(bank,seen)
    fingerprints.append([hashlib.sha256(c).digest() for c in colors])
header=ROOT/'engine/runner/tlk_cw_monkey_metadata.h'
text='/* Reviewed addresses and palette fingerprints only; no extracted game assets.\n * 30 exact anchored/indexed frame pairs; original colors verified in live CGRAM. */\n'
text+='static const unsigned cw_monkey_poses[]={'+','.join(hex(p) for p in poses)+'};\n'
text+='static const unsigned cw_monkey_descriptors[]={'+','.join(hex(p) for p in descriptors)+'};\n'
text+='static const unsigned char cw_monkey_palette_hashes[2][2][32]={\n'
for hashes in fingerprints:text+='    {'+','.join('{'+','.join('0x%02x'%b for b in h)+'}' for h in hashes)+'},\n'
text+='};\n';header.write_text(text)
out=ROOT/'build/cant-wait439-metadata';out.mkdir(exist_ok=True)
paths=[reference,palettes,header,ROOT/'tools/prepare_cant_wait439_metadata.py']
(out/'report.json').write_text(json.dumps(dict(result='VERIFIED_METADATA',shared_frames=len(poses),descriptors=[hex(d) for d in descriptors],palette_sources=[[hex(p) for p in offsets] for offsets in sources],scope='Palette fingerprints checked against original native live CGRAM; native draw palette uses bits1..3, not PPU attribute bits9..11. Previous436/437 diagnostic palette0 values are parser errors, not game state.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('VERIFIED_METADATA',len(poses),len(descriptors),flush=True)
