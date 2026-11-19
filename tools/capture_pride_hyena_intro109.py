"""Original MD battle music and opening weak-jump calls during ordinary play."""
import csv
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from pride_arena_history import bound

out=ROOT/'build/pride-hyena-intro109';out.mkdir()
plan=ROOT/'build/pride-md-hyena-normal-repeat-plan/report.json';bound(plan)
tape=plan.parent/'selected-inputs.json';pads=json.loads(tape.read_text())
reference=ROOT/'build/pride-hyena-motion87/md/normal/frames.json';expected={r['field']:r for r in json.loads(reference.read_text())}
game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
for port in (0,1):game.core.retro_set_controller_port_device(port,513)
library=ROOT/'build/pride-audio-inventory/trace.dll';trace=C.CDLL(str(library));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
rows=[];matched=[];actor=0x9a4e
try:
    for field,pad in enumerate(pads[:4075],1):
        trace.md_commands_frame(field);game.step(pad);game.samples.clear()
        if field<3700:continue
        word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
        longword=lambda at:word(at)<<16|word(at+2)
        draw=word(actor+12)
        row=dict(field=field,descriptor=longword(actor+4)&0xffffff,action=longword(actor+0x30)&0xffffff,
                 x=word(actor+8),y=word(actor+10),timer=word(actor+0x2c),tag=word(actor+0x2e),
                 player_x=word(0x93d6),player_y=word(0x93d8),vx_q16=longword(actor+0x38),vy_q16=longword(actor+0x3c),
                 health=word(actor+0x2a),cycle=word(actor+0x28),facing=word(actor+0x20),pose=longword(draw+10)&0xffffff)
        if field in expected:
            ref=expected[field];matched.append(all(row[k]==ref[k] for k in ('action','x','y','timer','tag','health','cycle','facing','pose')))
        rows.append(row)
        if field in (3900,3950,3951,3972):png(out/f'{field}.png',*game.image)
finally:trace.md_commands_close();game.close()
calls=list(csv.DictReader((out/'commands.csv').open()));battle=[r for r in calls if r['selector']=='1' and int(r['value'])==134]
jumps=[r for r in rows if r['action']==0x19ba8c and r['field']>3700]
(out/'frames.json').write_text(json.dumps(rows,indent=2)+'\n')
checks=dict(all376_intro_fields=len(rows)==376,all126_prior_motion_fields_exact=len(matched)==126 and all(matched),
            original_battle_music_observed=bool(battle),first_weak_jump_parameters=jumps[0]['vx_q16']==0xfffc0000 and jumps[0]['vy_q16']==0xfffe0000,
            first_music_matches_first_weak_jump=int(battle[0]['frame'])==jumps[0]['field'])
paths=[Path(__file__),plan,tape,reference,library,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_HYENA_INTRO_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,
    battle_music_calls=battle,first_weak_jump=jumps[0],guest_or_rom_edits=False,production_changed=False,
    scope='Original ordinary MD Normal encounter opening; frame clock and first parameters, not a matched SNES player route or proof of a runtime audio bug.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Original intro',checks,'battle',battle,'first jump',jumps[0],flush=True)
