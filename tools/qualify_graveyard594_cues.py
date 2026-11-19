"""Verify original sound calls, native countdown seams and guarded action metadata."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
native=[(0xc19ab0,0x35),(0xc19f23,0x35),(0xc48411,0x35),(0xc17986,0x1d),(0xc2d248,0x22),(0xc5565b,0x12)]
for p,e in native:assert s[(p&0x3fffff)-7:p&0x3fffff]==b'\xf4'+e.to_bytes(2,'little')+bytes.fromhex('22ec2cc2')
md=[(0x1a442c,105,0x228a),(0x1a1af2,105,0x228a),(0x1a1718,127,0x228a),(0x1a0a36,2,0x2210),(0x1a2be0,171,0x228a),(0x1a2cb2,92,0x228a),(0x18fae6,117,0x228a)]
for p,v,w in md:assert m[p-10:p]==bytes.fromhex('3f3c')+v.to_bytes(2,'big')+bytes.fromhex('4eb9')+w.to_bytes(4,'big')
assert s[0x19ac4:0x19ac9]==bytes.fromhex('b1003a9100') and s[0x19f84:0x19f89]==bytes.fromhex('b1003a9100')
assert s[0x22cbf:0x22cc1]==bytes.fromhex('a304')
assert m[0x1a1ade:0x1a1ae4]==bytes.fromhex('0c690001002c') and m[0x1a1704:0x1a170a]==bytes.fromhex('0c690001002c')
shake=[0xc58d90,0xc58da2,0xc58db4,0xc58dce,0xc58de8,0xc58e02]
for p in shake:assert s[p&0x3fffff:(p&0x3fffff)+3]==bytes.fromhex('d1d7c0') and 0xc19788<=int.from_bytes(s[(p&0x3fffff)+13:(p&0x3fffff)+16],'little')<=0xc198ad
header=ROOT/'engine/runner/tlk_graveyard_audio_metadata.h'
header.write_text('/* Reviewed original audio owners; graphics coverage remains separate. */\nstatic const unsigned gy_shake_descriptors[]={'+','.join(hex(p) for p in shake)+'};\nstatic const unsigned gy_platform_descriptors[]={0xc58e1c,0xc58e36,0xc58e50,0xc58e6a};\nstatic const unsigned gy_vulture_descriptors[]={0xc58cca,0xc58cd8,0xc58ce6,0xc58cf2,0xc58d00};\n')
refs=[ROOT/'build/graveyard588-audio/report.json',ROOT/'build/graveyard591-cue-owners/report.json',ROOT/'build/graveyard592-native-owners/report.json'];[bound(p) for p in refs]
out=ROOT/'build/graveyard594-cues';out.mkdir(exist_ok=True);paths=[Path(__file__),header,*refs]
(out/'report.json').write_text(json.dumps(dict(result='VERIFIED',native_calls=[dict(caller=hex(p),event=e) for p,e in native],md_calls=[dict(caller=hex(p),value=v,wrapper=hex(w)) for p,v,w in md],scope='Original calls and exact actor census; bone actions199F9/19E97 already own30/26-update countdowns. Selected MD creaks occur when their original decrement reaches zero. C22CBF group11 stop on owned C58D44/C2D1D3 marks pillar impact. No guest state/timer changes or host event latch is needed.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('VERIFIED',flush=True)
