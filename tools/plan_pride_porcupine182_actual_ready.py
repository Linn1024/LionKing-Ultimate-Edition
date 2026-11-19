"""Use actual actor/health RAM, not a latched UI descriptor, for boot timing."""
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
previous=ROOT/'build/pride-porcupine180-ready/report.json';old=bound(previous);assert old['result']=='PLANNED'
raw=ROOT/'build/pride-porcupine181-ready-aligned/easy/samples.bin'
found=None
with raw.open('rb') as f:
    while header:=f.read(16):
        magic,field,pad,size=struct.unpack('<4I',header);assert magic==0x4b4c5443 and size==0x20000
        ram=f.read(size);word=lambda at:struct.unpack_from('<H',ram,at)[0]
        if word(0x2004)==4 and word(0xb21b)==64 and word(0xb21d)>=1248 and int.from_bytes(ram[0xdf:0xe2],'little')==0xc00387:
            found=dict(field=field,health=word(0x2004),player=[word(0xb21b),word(0xb21d)],spares=word(0x1ffaa));break
assert found, 'No actual initial player in retained controller experiment'
original=ROOT/'build/pride-reset/fixed4/native/gates/allbugs-aot.ram';rows=[line.split() for line in original.read_text().splitlines()]
ready=next(int(r[0]) for r in rows if int(r[3],16)==4 and int(r[4],16)==64 and int(r[5],16)>=1248)
prefix=ROOT/'build/pride-difficulty-start2/snes/easy/ordinary.tape';prefix_fields=prefix.stat().st_size//2
target=found['field']+(943-ready)-1;trim=prefix_fields-target
out=ROOT/'build/pride-porcupine182-actual-ready';out.mkdir()
paths=[Path(__file__),previous,raw,original,prefix]
(out/'report.json').write_text(json.dumps(dict(result='PLANNED',checks=dict(actual_initial_player_found=True,only_final_neutral_suffix_removed=0<trim<400),
    original_ready_field=ready,actual_easy_ready=found,target_easy_prefix_fields=target,trim_fields=trim,
    correction='180 UI owner/health fields were latched before the actual actor was allocated.181 first process exited0 but its parser rejected zero initial health; raw retained. This plan uses actual full RAM with player64 and initialized health4, without guest writes. Other difficulty offsets still require actual observed confirmation.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('ACTUAL',found,'target',target,'trim',trim,flush=True)
