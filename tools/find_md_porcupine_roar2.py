"""Observe original committed attacks during ordinary roar-input protocols."""
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


def main():
    out=ROOT/'build/md-porcupine-roar2';out.mkdir()
    original_source=ROOT/'tools/md_porcupine_contact_trace.c';text=original_source.read_text()
    replacements=[('&& address!=0x19a81c)return;','&& address!=0x19a81c && address!=0x19a086)return;'),
        (r'health,player_x,player_y\n',r'health,player_x,player_y,roar_active,player_action\n'),
        (r'%06x,%u,%u,%u\n',r'%06x,%u,%u,%u,%u,%06x\n'),
        ('word(0xccf6),word(player+8),word(player+10));','word(0xccf6),word(player+8),word(player+10),word(0xccf4),pointer(player+0x30));')]
    for before,after in replacements:
        assert text.count(before)==1,before;text=text.replace(before,after)
    source=out/'trace.c';source.write_text(text);library=out/'trace.dll'
    command=['C:/mingw32/bin/gcc.exe','-O2','-Werror=format','-shared','-static-libgcc',str(source),'-o',str(library)]
    subprocess.run(command,cwd=ROOT,check=True)
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        inputs=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    trace=C.CDLL(str(library));trace.contact_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    cases={}
    for label,delay,roar in [('turn-control',32,False),('roar32',32,True),('roar48',48,True),('roar64',64,True)]:
        folder=out/label;folder.mkdir();game=MdLab()
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
        assert trace.contact_trace_init(game.core._handle,str(folder/'calls.csv').encode())
        protocol=[0]*delay+[1<<6]+([1<<0] if roar else [0])*20+[0]*(200-delay-21)
        def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
        def ptr(at):return (word(at)<<16|word(at+2))&0xffffff
        index=0;branch=0;polled=[];log=[];captured=False
        try:
            for field in range(1,1997):
                pad=inputs[index] if field<=1796 else protocol[min(branch,len(protocol)-1)]
                trace.contact_trace_field(field);game.step(pad)
                if trace.contact_trace_polled():
                    polled.append(pad)
                    if field<=1796:index+=1
                    else:branch+=1
                if field>=1796:
                    player=ptr(0xcd46)&65535
                    log.append(dict(field=field,health=word(0xccf6),roar=word(0xccf4),action=hex(ptr(player+0x30)),x=word(player+8),y=word(player+10)))
                    if word(0xccf4) and not captured:png(folder/'roar-pulse.png',*game.image);captured=True
            png(folder/'final.png',*game.image)
        finally:trace.contact_trace_close();game.close()
        (folder/'polled.libretro.tape').write_bytes(struct.pack('<'+'H'*len(polled),*polled))
        (folder/'player.json').write_text(json.dumps(log,indent=2)+'\n')
        rows=list(csv.DictReader((folder/'calls.csv').open()))
        attacks=[r for r in rows if r['pc']=='19a446' and r['action']=='19a446']
        active=[r for r in attacks if int(r['roar_active'])]
        transitions=[]
        for a in active:
            following=[b for b in attacks if int(b['field'])==int(a['field'])+1 and b['actor']==a['actor']]
            if following:
                b=following[0]
                transitions.append(dict(before=a,after=b,countdown_continues=int(b['wait'])==int(a['wait'])-1 if int(a['wait'])>0 else int(b['timer'])==int(a['timer'])-1))
        cases[label]=dict(roar_protocol=roar,delay=delay,active_attack_observations=active,transitions=transitions,
            roar_reaction_calls=[r for r in rows if r['pc']=='19a086'],final_health=log[-1]['health'],
            health_drops=[(b['field'],a['health'],b['health']) for a,b in zip(log,log[1:]) if b['health']<a['health']])
        print(label,'active',[(r['field'],r['timer'],r['roar_active']) for r in active],
              'continued',[r['countdown_continues'] for r in transitions],flush=True)
    paths=[Path(__file__),original_source,source,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',movie,reference,
           ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='OBSERVED' if any(r['active_attack_observations'] for r in cases.values()) else 'NO_ACTIVE_ATTACK_ROAR',
        cases=cases,compile_command=command,ordinary_controls_only=True,guest_rom_or_rng_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
