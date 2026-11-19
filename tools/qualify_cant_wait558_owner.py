"""Resolve the actual odd-aligned reaction actor and the complete original audio-owner family."""
import json,struct
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait557-reaction-owner/report.json';bound(reference)
ram=(reference.parent/'wram.bin').read_bytes();w=lambda at:struct.unpack_from('<H',ram,at)[0];a=lambda at:int.from_bytes(ram[at:at+3],'little')
s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
descriptors=[p|0xc00000 for p in range(0x58b48,0x58c08) if s[p:p+3]==bytes.fromhex('f349c4') and int.from_bytes(s[p+6:p+9],'little') in (0xc43f0d,0xc4427c)]
assert len(descriptors)==16
actors=[]
for actor in range(0x8000,0xff81):
    if a(actor+0x30)!=0xc455ac or a(actor+4) not in descriptors:continue
    draw=w(actor+12);assert 0x8000<=draw<=0xffe8 and w(draw+4)==actor+8
    actors.append(dict(actor=hex(actor),descriptor=hex(a(actor+4)),counter=w(actor+0x2e),draw=hex(draw)))
assert any(x['actor']=='0xb493' and x['descriptor']=='0xc58b90' and x['counter']==18 for x in actors)
meta=ROOT/'engine/runner/tlk_cw_audio_metadata.h';meta.write_text('/* Complete original C449F3 monkey owner family for sound; artwork coverage is separate. */\nstatic const unsigned cw_audio_monkey_descriptors[]={'+','.join(hex(p) for p in descriptors)+'};\n')
out=ROOT/'build/cant-wait558-owner-qualified';out.mkdir(exist_ok=True);paths=[Path(__file__),reference,reference.parent/'wram.bin',meta]
(out/'report.json').write_text(json.dumps(dict(result='REACTION_OWNER_VERIFIED',actors=actors,descriptors=[hex(p) for p in descriptors],scope='Actual B493/C58B90 is absent from the eight-owner graphics subset. All16 original monkey descriptors use common initializerC449F3 and the two original monkey default images. 557 inspected only even addresses; native task addresses are odd, so derived save reconstruction scans both alignments. No game rerun or behavior change for this qualification.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(actors,[hex(p) for p in descriptors],flush=True)
