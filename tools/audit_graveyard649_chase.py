"""Compare original flying-vulture pursuit exits and phase delays; no engine change or route replay."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
def bind(rom,address,value):assert rom[address:address+len(bytes.fromhex(value))]==bytes.fromhex(value),hex(address)
bind(s,0x17553,'a522c99001f00e300c22237cc1');bind(m,0x1a062a,'0c6e0190ffe26f00000e4eb9001a0c58')
bind(s,0x174dc,'a01c00b10038e52e');bind(m,0x1a05a4,'3229001c926effee')
bind(s,0x177fd,'a91e00a02c009100');bind(m,0x1a08ca,'337c001e002c')
bind(s,0x17834,'a522d00c221179c1');bind(m,0x1a0904,'0c6e0000fff86600000e4eb9001a09d8')
for a in (0x17a8f,0x17aba):bind(s,a,'f43c0022e773c1')
for a in (0x1a0b2a,0x1a0b56):bind(m,a,'3f3c003c4eb9001a04de')
bind(s,0x17742,'a52618693000850ca52ec50cf0193017a5361013a538c90200d00c22b277c1')
bind(m,0x1a080c,'342effe6064200303e2effeebe426f0000220c6e0000fff66c0000180c6e0002fff86600000e4eb9001a089a')
out=ROOT/'build/graveyard649-chase-rules';out.mkdir(exist_ok=True)
paths=[Path(__file__),ROOT/'engine/runner/tlk_graveyard_gameplay.c',ROOT/'tools/snes_disassemble.py',ROOT/'tools/md_disassemble.py']
report=dict(result='MATCHING_PURSUIT_RULES',rules=dict(cruising_home_x_limit={'snes':400,'md':400,'trigger':'absolute current X minus saved initial X exceeds400; enter return state, not an immediate despawn'},post_dive_delay_updates={'snes':60,'md':60,'meaning':'permits another dive only after the countdown plus facing/position/animation conditions; not a chase expiration timer'},pre_dive_slowdown_updates={'snes':30,'md':30},dive_exit='Both compare current vulture X against current Simba X in the attack direction; passing Simba returns to circling. Initial Simba Y is saved for the dive; horizontal Simba position is read again each update.',dive_start='Both require expired delay, appropriate animation phase and bird48px beyond Simba in the relevant facing direction. Other vulture types retain distinct attacks.'),scope='Original ROM control-flow review of flying-vulture circling/slowdown/dive/return states C173E7/C177B2/C17911/C17C23 versus1A04DE/1A089A/1A09D8/1A0C58. No single fixed total pursuit duration. Actual encounter length still depends on movement, contacts, repeated attack opportunities and ordinary offscreen culling. No identical-input original-platform duration measurement or universal all-vulture parity claim. Current installed644 retains native pursuit; selected MD gameplay leaves only alter health/bounds.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],report['rules'],flush=True)
