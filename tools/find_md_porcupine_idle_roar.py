"""Seek original idle roar responses using ordinary approaches before the stomp."""
import csv
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from pride_arena_history import bound


def main():
    out=ROOT/'build/md-porcupine-idle-roar';out.mkdir()
    previous=ROOT/'build/md-porcupine-roar3/report.json';bound(previous)
    original_source=previous.parent/'trace.c';text=original_source.read_text()
    before='&& address!=0x19a086)return;'
    assert text.count(before)==1
    text=text.replace(before,'&& address!=0x19a086 && address!=0x19a128 && address!=0x19a07e)return;')
    source=out/'trace.c';source.write_text(text);library=out/'trace.dll'
    command=['C:/mingw32/bin/gcc.exe','-O2','-Werror=format','-shared','-static-libgcc',str(source),'-o',str(library)]
    subprocess.run(command,cwd=ROOT,check=True)
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2';reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        inputs=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    trace=C.CDLL(str(library));trace.contact_trace_init.argtypes=[C.c_void_p,C.c_char_p];cases={}
    for anchor in (1770,1776,1780):
        for delay in (32,56,80):
            label=f'{anchor}-{delay}';folder=out/label;folder.mkdir();game=MdLab()
            game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
            for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
            assert trace.contact_trace_init(game.core._handle,str(folder/'calls.csv').encode())
            def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
            def ptr(at):return (word(at)<<16|word(at+2))&0xffffff
            index=branch=0;polled=[];players=[];protocol=[0]*delay+[1<<1]*20+[0]*(200-delay-20)
            try:
                for field in range(1,anchor+201):
                    pad=inputs[index] if field<=anchor else protocol[min(branch,199)]
                    trace.contact_trace_field(field);game.step(pad)
                    if trace.contact_trace_polled():
                        polled.append(pad)
                        if field<=anchor:index+=1
                        else:branch+=1
                    if field>anchor:
                        p=ptr(0xcd46)&65535
                        players.append(dict(field=field,health=word(0xccf6),x=word(p+8),y=word(p+10),action=hex(ptr(p+0x30)),active=word(0xccf4)))
                png(folder/'final.png',*game.image)
            finally:trace.contact_trace_close();game.close()
            rows=list(csv.DictReader((folder/'calls.csv').open()))
            helper=[r for r in rows if r['pc']=='19a086' and int(r['roar_active'])]
            installed=[r for r in rows if r['pc']=='19a07e']
            (folder/'player.json').write_text(json.dumps(players,indent=2)+'\n')
            (folder/'polled.libretro.tape').write_bytes(struct.pack('<'+'H'*len(polled),*polled))
            cases[label]=dict(idle_helpers=helper,installed=installed,active_fields=[r['field'] for r in players if r['active']],final_health=players[-1]['health'])
            print(label,'active',cases[label]['active_fields'],'helpers',len(helper),'installed',[(r['field'],r['timer'],r['actor']) for r in installed],flush=True)
    paths=[Path(__file__),previous,original_source,source,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',movie,reference,
        ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='OBSERVED_IDLE_RESPONSE' if any(c['installed'] for c in cases.values()) else 'NO_IDLE_RESPONSE_FOUND',cases=cases,
        compile_command=command,ordinary_controls_only=True,guest_rom_or_rng_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
