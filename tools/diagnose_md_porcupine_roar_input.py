"""Observe raw/translated original inputs before interpreting a failed roar attempt."""
import ctypes as C
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from md_lab import MdLab
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/md-porcupine-roar-input';out.mkdir()
    tape=ROOT/'build/md-porcupine-contact/neutral/polled.libretro.tape'
    raw=tape.read_bytes();pads=struct.unpack('<'+'H'*(len(raw)//2),raw)
    library=ROOT/'build/md-porcupine-contact/trace.dll';trace=C.CDLL(str(library))
    trace.contact_trace_init.argtypes=[C.c_void_p,C.c_char_p];cases={}
    for button in (0,1,8):
        folder=out/str(button);folder.mkdir();game=MdLab()
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        assert trace.contact_trace_init(game.core._handle,str(folder/'calls.csv').encode())
        def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
        def ptr(at):return (word(at)<<16|word(at+2))&0xffffff
        index=branch=0;rows=[];protocol=[0]*32+[1<<6]+[1<<button]*20+[0]*150
        try:
            for field in range(1,1871):
                pad=pads[index] if field<=1796 else protocol[branch]
                trace.contact_trace_field(field);game.step(pad)
                if trace.contact_trace_polled():
                    if field<=1796:index+=1
                    else:branch+=1
                if field>=1815:
                    p=ptr(0xcd46)&65535
                    rows.append(dict(field=field,pad=hex(pad),held=hex(word(0xccb4)),new=hex(word(0xccba)),
                        strength=word(0xccf2),active=word(0xccf4),action=hex(ptr(p+0x30)),timer=word(p+0x2c),flags46=word(p+0x46)))
        finally:trace.contact_trace_close();game.close()
        (folder/'inputs.json').write_text(json.dumps(rows,indent=2)+'\n');cases[str(button)]=rows
        print(button,[r for r in rows if r['new']!='0x0'][:6],flush=True)
    paths=[Path(__file__),tape,library,ROOT/'tools/md_lab.py']
    report=dict(result='OBSERVED',cases=cases,guest_rom_or_rng_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
