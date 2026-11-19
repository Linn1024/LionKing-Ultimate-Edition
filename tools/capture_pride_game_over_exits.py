"""Observe original Game Over dismissal/timeout from an ordinary arena route.

Run with .tools/python32/python.exe. Unique visible frames are compressed under
ignored build/; no guest/ROM edits or forced actors are used.
"""
import array
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='build/pride-game-over-exits-original');parser.add_argument('--held',action='store_true');args=parser.parse_args()
    out=ROOT/args.output;out.mkdir();(out/'frames').mkdir()
    source=ROOT/'build/pride-final-arena-original/report.json';old=bound(source)
    prior=ROOT/'build/pride-final-menu-art-original/report.json';bound(prior)
    inputs=source.parent/'inputs.json';pads=json.loads(inputs.read_text());fatal=old['fatal_field']
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_serialize_size.restype=C.c_size_t
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    checks={};cases={};unique=set()
    try:
        for pad in pads[:fatal-1]:game.step(pad);game.samples.clear()
        size=game.core.retro_serialize_size();state=C.create_string_buffer(size)
        assert game.core.retro_serialize(state,size);(out/'prefatal.state').write_bytes(state.raw)
        scenarios=[('held100',100,256),('held123',123,256),('held124',124,256)] if args.held else [
            ('none',None,0),('a100',100,256),('a121',121,256),('a122',122,256),('a123',123,256),('a124',124,256),('a140',140,256),('start140',140,8)]
        for name,pressed,button in scenarios:
            assert game.core.retro_unserialize(state,size);folder=out/name;folder.mkdir();rows=[]
            for age in range(401):
                down=pressed is not None and pressed<=age<=(140 if args.held else pressed)
                pad=pads[fatal-1] if age==0 else (button if down else 0)
                game.step(pad);game.samples.clear()
                if age<90:continue
                data,w,h,pitch,fmt=game.image;assert (w,h,fmt)==(320,224,2)
                tight=b''.join(data[y*pitch:y*pitch+640] for y in range(224));sha=hashlib.sha256(tight).hexdigest()
                if sha not in unique:(out/'frames'/(sha+'.rgb565.z')).write_bytes(zlib.compress(tight));unique.add(sha)
                word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
                rows.append(dict(age=age,frame_sha256=sha,black=not any(tight),cram=bytes(game.cram).hex(),
                    registers=list(game.reg),level=word(0xccce),health=word(0xccf6),lives=word(0xccee),credits=word(0xccda)))
                if age in (118,124,140,150,159,160,220,300,320,322,323,324,330,340,360,400):
                    png(folder/f'{age}.png',tight,320,224,640,2)
                if name=='none' and age in (118,140,160,220):
                    reference=prior.parent/'game-over'/str(age)/'window.png'
                    actual=[(((v>>11)&31)*255//31,((v>>5)&63)*255//63,(v&31)*255//31) for v in array.array('H',tight)]
                    checks[f'original_menu{age}_matches']=pixels(reference)==(320,224,actual)
            base=next(r['cram'] for r in rows if r['age']==118)
            fade=next((r['age'] for r in rows if r['age']>=124 and r['cram']!=base),None)
            black=next((r['age'] for r in rows if fade is not None and r['age']>=fade and r['black']),None)
            title=next((r['age'] for r in rows if black is not None and r['age']>black and not r['black']),None)
            cases[name]=dict(pressed_age=pressed,held_through=140 if args.held else pressed,button=button,fade=fade,black=black,next_picture=title,frames=rows)
            print(name,'fade',fade,'black',black,'next picture',title,flush=True)
    finally:game.close()
    paths=[Path(__file__),source,prior,inputs,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
    report=dict(result='OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
        ordinary_route=True,guest_or_rom_edits=False,unique_visible_frames=len(unique),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');assert all(checks.values())


if __name__=='__main__':main()
