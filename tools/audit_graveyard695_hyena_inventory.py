"""Bounded original regular-hyena sound-call inventory; distinguish lizard defeat and boss music."""
import json,re,sys
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
sys.path.insert(0,str(ROOT/'.tools/pythonlibs'))
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5');cpu=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
out=ROOT/'build/graveyard695-hyena-inventory';out.mkdir(exist_ok=True)
ins=list(cpu.disasm(m[0x19a64a:0x19bd2e],0x19a64a));assert ins[-1].address+ins[-1].size==0x19bd2e
calls=[]
for i,x in enumerate(ins):
 if x.mnemonic!='jsr' or x.op_str not in ('$2210.l','$228a.l','$22a6.l','$2d0000.l'):continue
 previous=ins[i-1];match=re.fullmatch(r'#\$([0-9a-f]+), -\(a7\)',previous.op_str);assert previous.mnemonic=='move.w' and match
 calls.append(dict(pc=hex(x.address),wrapper=x.op_str,value=int(match[1],16),kind='pcm' if x.op_str=='$2210.l' else 'music' if x.op_str=='$22a6.l' else 'fm'))
def sounds_in(start,end):return [hex(x.address) for x in cpu.disasm(m[start:end],start) if x.mnemonic=='jsr' and x.op_str in ('$2210.l','$228a.l','$22a6.l','$2d0000.l')]
runtime=ROOT/'build/graveyard694-hyena-sounds/report.json';r=bound(runtime)
checks=dict(three_vocal_programs={x['value'] for x in calls if x['kind']=='pcm'}=={3,4,7},no_other_hyena_fx_calls=all(x['kind']!='fm' for x in calls),puffed_defeat_is_outside_hyena_actions=not sounds_in(0x19b904,0x19ba8c),physical_jump_has_no_voice=not sounds_in(0x19ba8c,0x19bc60),socket_reveal_has_no_voice=not sounds_in(0x19ab1e,0x19ad6c),boss_calls_are_music=all(x['value']==134 for x in calls if x['kind']=='music'),current_runtime_checks_pass=r['result']=='PASS')
(out/'listing.txt').write_text('\n'.join(f'{x.address:06x} {x.mnemonic} {x.op_str}' for x in ins)+'\n')
paths=[Path(__file__),runtime,ROOT/'build/graveyard691-original-jump-voice/report.json',ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/tlk_hyena_audio.c']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,original_calls=calls,scope='Regular young-Simba hyena action family19A64A..19BD2E, including skull entry, damage and death. Original ROM verified. PCM3 taunt,4 reaction,7 pant; no vocal cue on ordinary leap/hit/death. FM165 belongs to a different shared enemy-death family19C554 and is not a missing hyena cue. Boss134 calls are music. Runtime694 checks current installed684; no later adult-enemy or universal timing claim.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'listing.txt':digest(out/'listing.txt')}),indent=2)+'\n');print(checks,calls,flush=True)
