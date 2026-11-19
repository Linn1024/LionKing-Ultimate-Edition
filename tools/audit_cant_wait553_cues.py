"""Bind original rhino/contact/reaction sounds and the audible reaction phase difference."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait547-audio/report.json';r=bound(reference)
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
native=[(0xc2e99f,0x11),(0xc44dee,0xb),(0xc452e3,0xb),(0xc45556,0xb),(0xc45610,0x1a)]
for caller,event in native:
    p=caller&0x3fffff;assert s[p-7:p]==bytes.fromhex('f4')+event.to_bytes(2,'little')+bytes.fromhex('22ec2cc2')
md=[(0x19ce94,106,0x228a),(0x19d8ac,119,0x228a),(0x19dca8,119,0x228a),(0x19dea6,119,0x228a),(0x19df6a,8,0x2210)]
for caller,value,wrapper in md:assert m[caller-10:caller]==bytes.fromhex('3f3c')+value.to_bytes(2,'big')+bytes.fromhex('4eb9')+wrapper.to_bytes(4,'big')
assert s[0x455fe:0x45601]==bytes.fromhex('a91200') and m[0x19df30:0x19df36]==bytes.fromhex('337c0012002e')
groups={}
for event in (0xb,0x11,0x1a):groups[hex(event)]=sum(x['count'] for x in r['native_counts'] if int(x['event'],16)==event)
out=ROOT/'build/cant-wait553-cues';out.mkdir(exist_ok=True)
paths=[Path(__file__),reference,ROOT/'build/cant-wait549-md-actors/report.json',ROOT/'engine/runner/tlk_cw_monkey_metadata.h']
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_CUE_PHASES_VERIFIED',native_calls=[dict(caller=hex(p),event=hex(e)) for p,e in native],md_calls=[dict(caller=hex(p),value=v,wrapper=hex(w)) for p,v,w in md],native_counts=groups,reaction=dict(native_state='0xc455ac',counter_offset='0x2e',wait=18,native_voice='At reaction entry before the countdown',md_voice='After the 18-update reaction countdown'),scope='Source calls and retained ordinary original command/actor evidence. Native reaction gameplay already has the same countdown; move selected MD voice to its end, without changing monkey behavior or adding a fixed wall-clock delay.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('VERIFIED',groups,flush=True)
