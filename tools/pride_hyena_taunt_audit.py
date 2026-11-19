"""Observe original MD Pride hyena taunts after stopping ordinary movie input.

Requires the local original movie and matching lag reference. No game fields,
actor callbacks, positions, ROM bytes or CPU registers are changed.
"""
import argparse
import csv
import ctypes as C
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab, ROOT, png
from md_replay_movie import movie_inputs
from pride_sprite_catalog import read_rom


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stop-at',type=int,default=3900)
    parser.add_argument('--frames',type=int,default=5000)
    parser.add_argument('--out',type=Path,default=ROOT/'build/hyena-taunt-original')
    args=parser.parse_args()
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    pads,_,settings=movie_inputs(movie)
    with (ROOT/'build/md-next-levels-reference/ram.csv').open() as stream:
        polled=[pads[int(row['frame'])-1] for row in csv.DictReader(stream)
                if row['lag']=='0' and int(row['frame'])<=len(pads)]
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    args.out.mkdir(exist_ok=True,parents=True)
    game=MdLab()
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device(0,device)
    game.core.retro_set_controller_port_device(1,device)
    trace=C.CDLL(str(ROOT/'build/md_commands.dll'))
    trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_commands_init(game.core._handle,str(args.out/'commands.csv').encode())
    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
    index=0;rows=[];captured=False
    try:
        for frame in range(1,args.frames+1):
            trace.md_commands_frame(frame)
            game.step(polled[index] if frame<=args.stop_at else 0)
            if trace.md_commands_polled():index+=1
            actors=[]
            for actor in range(0x944e,0xa3ce,0x80):
                state=word(actor+0x30)<<16|word(actor+0x32)
                if state==0x19b3a8:
                    draw=word(actor+12)
                    actors.append({'actor':actor,'state':state,'counter':word(actor+0x2e),
                                   'pose':(word(draw+10)<<16|word(draw+12))&0xffffff,
                                   'palette':(word(draw+8)>>13)&3})
            if actors and word(0xccce)==1:
                rows.append({'frame':frame,'level_register':1,'actors':actors})
                if not captured:
                    for name in ('work_ram','vram','cram','reg','vsram'):
                        (args.out/(name+'.bin')).write_bytes(bytes(getattr(game,name)))
                    png(args.out/'first-taunt.png',*game.image);captured=True
    finally:
        trace.md_commands_close();game.close()
    commands=[row for row in csv.DictReader((args.out/'commands.csv').open())
              if row['selector']=='19' and row['value']=='3' and row['outer_caller']=='19b3fe']
    assert rows and commands,'No ordinary-input original Pride taunt observed'
    frames={row['frame'] for row in rows}
    assert all(int(row['frame']) in frames for row in commands),'Cue outside observed Pride action'
    assert {actor['palette'] for row in rows for actor in row['actors']}=={3}
    report={'result':'PASS','scope':__doc__,'source':'https://tasvideos.org/10612S',
            'stop_at':args.stop_at,'frames':args.frames,'taunt_frames':len(rows),
            'first_taunt_frame':rows[0]['frame'],'observed_pcm3_calls':len(commands),
            'commands':commands,'observations':rows}
    (args.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original Pride taunt:',len(rows),'normal fields,',len(commands),'PCM3 calls PASS',flush=True)


if __name__=='__main__':main()
