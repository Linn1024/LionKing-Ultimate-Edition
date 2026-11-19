"""Attempt a fresh jump on the original MD pending-damage update."""
import ctypes as C
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab,png


def main():
    out=ROOT/'build/md-porcupine-pending-jump';out.mkdir()
    reference=ROOT/'build/md-porcupine-contact/report.json';old=bound(reference)
    tape=reference.parent/'left8/polled.libretro.tape'
    data=tape.read_bytes();pads=struct.unpack('<'+'H'*(len(data)//2),data)
    library=reference.parent/'trace.dll';trace=C.CDLL(str(library))
    trace.contact_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    assert trace.contact_trace_init(game.core._handle,str(out/'calls.csv').encode())
    def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
    def ptr(at):return (word(at)<<16|word(at+2))&0xffffff
    index=0;jump_field=None;log=[];recording=[]
    try:
        for field in range(1,1997):
            pad=pads[index] if field<=1867 else (1<<8 if jump_field is None else 0)
            trace.contact_trace_field(field);game.step(pad)
            if trace.contact_trace_polled():
                recording.append(pad)
                if field<=1867:index+=1
                elif jump_field is None:jump_field=field
            if field>=1865:
                victim=ptr(0xcd46)&65535
                log.append(dict(field=field,health=word(0xccf6),flags=game.work_ram[(victim+0x43)^1],
                    attacker=hex(ptr(victim+0x24)),action=hex(ptr(victim+0x30)),x=word(victim+8),y=word(victim+10)))
            if field==1868:png(out/'damage-update.png',*game.image)
    finally:trace.contact_trace_close();game.close()
    rows={r['field']:r for r in log};drop=[(b['field'],a['health'],b['health']) for a,b in zip(log,log[1:]) if b['health']<a['health']]
    checks=dict(prefix_matches_original_branch=rows[1867]['health']==4 and rows[1867]['x']==453 and rows[1867]['y']==937,
                original_damage_pending=bool(rows[1867]['flags']&4) and rows[1867]['attacker']=='0xff98ce',
                jump_on_next_polled_update=jump_field==1868,
                jump_does_not_erase_pending_damage=drop==[(1868,4,3)],
                one_unit_only=rows[1996]['health']==3)
    (out/'health.json').write_text(json.dumps(log,indent=2)+'\n')
    (out/'polled.libretro.tape').write_bytes(struct.pack('<'+'H'*len(recording),*recording))
    paths=[Path(__file__),reference,tape,library,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,first_jump_poll=jump_field,
                ordinary_poweron_inputs=True,guest_rom_or_rng_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),jump_field,drop,flush=True)


if __name__=='__main__':main()
