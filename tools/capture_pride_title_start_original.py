"""Trace original new-game interlude/caption with ordinary title inputs."""
import csv
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from capture_pride_title_readiness_contexts import picture
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-title-start-original2';out.mkdir()
    previous=ROOT/'build/pride-title-readiness-original/report.json';bound(previous)
    state=previous.parent/'game-over-timeout/before-input.state';raw=state.read_bytes()
    source=ROOT/'tools/md_title_trace.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-shared','-O2','-static-libgcc',str(source),'-o',str(library)],check=True)
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    trace=C.CDLL(str(library));trace.title_init.argtypes=[C.c_void_p,C.c_char_p]
    observations={};checks={}
    try:
        for label in ('neutral','right','second-start'):
            folder=out/label;folder.mkdir();blob=C.create_string_buffer(raw)
            assert game.core.retro_unserialize(blob,len(raw));assert trace.title_init(game.core._handle,str(folder/'caption.csv').encode())
            rows=[]
            for age in range(484,1116):
                pad=8 if age==515 or (label=='second-start' and age==600) else (128 if label=='right' and age>=516 else 0)
                trace.title_field(age);game.step(pad);game.samples.clear()
                word=lambda p:game.work_ram[p&65535]|game.work_ram[(p+1)&65535]<<8
                pointer=lambda p:(word(p)<<16|word(p+2))&0xffffff
                actor=word(0xcd48)  # Persistent player; 81C4 is transient current-actor scratch.
                data,w,h,pitch,fmt=game.image
                tight=b''.join(data[y*pitch:y*pitch+w*2] for y in range(h))
                rows.append(dict(age=age,level=word(0xccce),player=actor,x=word(actor+8),y=word(actor+10),
                                 action=pointer(actor+0x30),lit=sum(bool(tight[i] or tight[i+1]) for i in range(0,len(tight),2)),picture_sha256=picture(game)))
                if age in (515,550,600,650,700,750,800,850,900,950,1000,1050,1115):png(folder/f'{age}.png',*game.image)
            trace.title_close();calls=list(csv.DictReader((folder/'caption.csv').open()))
            checks[label+'_caption_task']=bool(calls) and all(r['descriptor']=='1d65ec' and r['pose']=='1d5dac' for r in calls)
            observations[label]=dict(first_caption=int(calls[0]['field']) if calls else None,last_caption=int(calls[-1]['field']) if calls else None,frames=rows)
            print(label,'caption',observations[label]['first_caption'],observations[label]['last_caption'],flush=True)
    finally:trace.title_close();game.close()
    paths=[Path(__file__),previous,state,source,ROOT/'tools/md_lab.py',ROOT/'tools/capture_pride_title_readiness_contexts.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                ordinary_inputs=True,guest_or_rom_edits=False,trace_library_sha256=digest(library),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
