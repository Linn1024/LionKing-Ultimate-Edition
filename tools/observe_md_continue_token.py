"""Observe original MD Continue-token phase holds on the credited ordinary route."""
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/md-continue-token-original';out.mkdir()
    source=ROOT/'tools/md_continue_token_trace.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)],check=True)
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv';pads,_,settings=movie_inputs(movie)
    with reference.open() as f:polled=[pads[int(r['frame'])-1] for r in csv.DictReader(f) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,device)
    trace=C.CDLL(str(library));trace.pickup_flight_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.pickup_flight_init(game.core._handle,str(out/'calls.csv').encode())
    index=0;captures=[];seen=set()
    def word(a):return game.work_ram[a]|game.work_ram[a+1]<<8
    def address(a):return (word(a)<<16|word(a+2))&0xffffff
    try:
        for field in range(1,3501):
            trace.pickup_flight_field(field);game.step(polled[index])
            if trace.pickup_flight_polled():index+=1
            if word(0xccce)!=1:continue
            for actor in range(0x944e,0xa3ce,0x80):
                if address(actor+0x30)!=0x19c604:continue
                draw=word(actor+12)
                if not 0x8000<=draw<=0xffe0:continue
                pose=address(draw+10)
                if pose in (0x18b3f8,0x18b430,0x18b468,0x18b4a0) and pose not in seen:
                    seen.add(pose);name=f'phase-{pose:x}-{field}.png';png(out/name,*game.image)
                    captures.append(dict(field=field,actor=actor,pose=pose,image=name))
    finally:trace.pickup_flight_close();game.close()
    rows=list(csv.DictReader((out/'calls.csv').open()))
    active=[r for r in rows if r['level']=='1' and r['callback']==r['action']=='19c604']
    actors={}
    for row in active:actors.setdefault(row['actor'],[]).append(row)
    groups={}
    for actor,values in actors.items():
        sequence=[]
        for row in values:
            if not sequence or sequence[-1]['pose']!=row['pose']:
                sequence.append(dict(pose=row['pose'],first_field=int(row['field']),last_field=int(row['field']),executed_updates=0))
            sequence[-1]['last_field']=int(row['field']);sequence[-1]['executed_updates']+=1
        groups[actor]=sequence
    interior=[g for sequence in groups.values() for g in sequence[1:-1] if g['pose'] in ('18b3f8','18b430','18b468','18b4a0')]
    checks=dict(ordinary_action_observed=bool(active),all_four_pose_families=all(any(r['pose']==p for r in active) for p in ('18b3f8','18b430','18b468','18b4a0')),
                at_least_one_full_cycle=len(interior)>=4,
                complete_phase_holds_six_executed_updates=bool(interior) and all(g['executed_updates']==6 for g in interior))
    paths=[Path(__file__),source,library,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',movie,reference]
    report=dict(result='PASS' if all(checks.values()) else 'OBSERVED_INCOMPLETE',checks=checks,executed_calls=len(active),groups=groups,captures=captures,
                input_polls=index,ordinary_input_no_guest_edits=True,production_code_changed=False,observer_neutrality_not_yet_qualified=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,'executed calls',len(active),flush=True)


if __name__=='__main__':main()
