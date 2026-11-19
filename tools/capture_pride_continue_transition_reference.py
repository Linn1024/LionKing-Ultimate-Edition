"""Capture the original confirmed Continue animation and incoming level fade."""
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-continue-transition-reference';out.mkdir()
    origin=ROOT/'build/pride-final-input-reference/prefatal.state'
    source=origin.parent/'report.json';assert bound(source)['result']=='OBSERVED'
    raw=origin.read_bytes();state=C.create_string_buffer(raw)
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    ages=(124,160,200,240,260,280,300,315,320,325,330,335,340,345,350,351,360,400,404,407,408,409,410,411,415,420,430)
    cases={}
    try:
        for confirm in (124,130):
            folder=out/str(confirm);folder.mkdir();assert game.core.retro_unserialize(state,len(raw))
            timeline=[];offsets=[]
            with (folder/'video.bin').open('wb') as video:
                for age in range(461):
                    game.step(128 if age==0 else (256 if age==confirm else 0));game.samples.clear()
                    data,w,h,pitch,fmt=game.image;assert (w,h)==(320,224) and fmt in (0,2)
                    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                    camera=word(0xcd36);player=word(camera+0x24) if 0x8000<=camera<0xffc8 else 0
                    entry=dict(age=age,cram=bytes(game.cram).hex(),health=word(0xccf6),camera=camera,player=player)
                    if 0x8000<=player<0xffc0:entry.update(x=word(player+8),y=word(player+10))
                    timeline.append(entry)
                    if age>=124:
                        offsets.append(dict(age=age,offset=video.tell(),bytes=len(data),width=w,height=h,pitch=pitch,format=fmt))
                        video.write(data)
                    if age in ages:
                        png(folder/f'{age}.png',*game.image)
            (folder/'timeline.json').write_text(json.dumps(timeline,indent=2)+'\n')
            cases[str(confirm)]=dict(confirm=confirm,video_frames=offsets)
            print('MD Continue',confirm,'captured through460',flush=True)
    finally:game.close()
    paths=[Path(__file__),origin,source,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
    report=dict(result='OBSERVED',cases=cases,guest_edits=False,public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
