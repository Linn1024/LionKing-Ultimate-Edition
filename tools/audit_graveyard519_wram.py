"""Extract current serialized WRAM only when its full logged SHA256 proves the bytes."""
import hashlib,json,re,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard511-checkpoint/report.json';r=bound(reference)
state=reference.parent/'entry.state';raw=state.read_bytes();log=reference.parent/'run.log';expected=re.findall(r'wram_sha256=([0-9a-f]+)',log.read_text())[-1]
needle=struct.pack('<HH',*r['scene']['player']);start=0;found=[]
while (at:=raw.find(needle,start))>=0:
    start=at+1;offset=at-0xb21b
    if offset<0 or offset+0x20000>len(raw):continue
    ram=raw[offset:offset+0x20000]
    if hashlib.sha256(ram).hexdigest()==expected:found.append(offset)
assert len(found)==1,found
offset=found[0];out=ROOT/'build/graveyard519-wram';out.mkdir(exist_ok=True);(out/'wram.bin').write_bytes(raw[offset:offset+0x20000])
paths=[Path(__file__),reference,state,log]
(out/'report.json').write_text(json.dumps(dict(result='WRAM_SHA_VERIFIED',state_offset=offset,wram_sha256=expected,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'wram.bin':digest(out/'wram.bin')}),indent=2)+'\n');print('VERIFIED',offset,expected,flush=True)
