"""Ordinary original-MD branches after first attack entry; no guest-state edits."""
import csv
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from md_replay_movie import movie_inputs


def main():
    out=ROOT/'build/md-porcupine-contact';out.mkdir()
    source=ROOT/'tools/md_porcupine_contact_trace.c';library=out/'trace.dll'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)]
    subprocess.run(command,cwd=ROOT,check=True)
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        inputs=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    trace=C.CDLL(str(library));trace.contact_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    cases={}
    for label,duration in [('neutral',0),('left4',4),('left8',8),('left16',16),('left32',32)]:
        folder=out/label;folder.mkdir();game=MdLab()
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
        assert trace.contact_trace_init(game.core._handle,str(folder/'calls.csv').encode())
        def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
        def ptr(at):return (word(at)<<16|word(at+2))&0xffffff
        index=0;branch_index=0;log=[];polled=[];captured=False
        try:
            for field in range(1,1997):
                pad=inputs[index] if field<=1796 else (1<<6 if branch_index<duration else 0)
                trace.contact_trace_field(field);game.step(pad)
                if trace.contact_trace_polled():
                    polled.append(pad)
                    if field<=1796:index+=1
                    else:branch_index+=1
                if field>=1796:
                    player=ptr(0xcd46)&65535
                    log.append(dict(field=field,health=word(0xccf6),x=word(player+8),y=word(player+10)))
                if trace.contact_trace_reactions() and not captured:
                    png(folder/'first-reaction.png',*game.image);captured=True
            png(folder/'final.png',*game.image)
        finally:trace.contact_trace_close();game.close()
        (folder/'polled.libretro.tape').write_bytes(struct.pack('<'+'H'*len(polled),*polled))
        (folder/'health.json').write_text(json.dumps(log,indent=2)+'\n')
        rows=list(csv.DictReader((folder/'calls.csv').open()))
        hits=[r for r in rows if r['pc']=='19a81c' and r['action']=='19a446']
        drops=[dict(field=b['field'],before=a['health'],after=b['health']) for a,b in zip(log,log[1:]) if b['health']<a['health']]
        cases[label]=dict(reactions=hits,health_drops=drops,first_health=log[0]['health'],last_health=log[-1]['health'],
                          prefix_polls=index,branch_polls=branch_index)
        print(label,len(hits),'reactions',drops,flush=True)
    paths=[Path(__file__),source,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',movie,reference,
           ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='OBSERVED_CONTACTS' if any(c['reactions'] for c in cases.values()) else 'NO_CONTACT_FOUND',
                cases=cases,compile_command=command,ordinary_poweron_inputs=True,guest_rom_or_rng_edits=False,
                full_original_port_equivalence_proven=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
