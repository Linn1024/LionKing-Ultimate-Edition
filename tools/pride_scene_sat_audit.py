"""Read original MD VRAM and internal SAT cache during checkpoint revival."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-scene-sat-full';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    sources=[Path(__file__),ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
             ROOT/'Lion King, The (World).md',ROOT/'build/md-next-levels-replay/frames.json',
             ROOT/'build/pride-death-timeline/report.json',ROOT/'.tools/genesis-plus-gx/core/vdp_render.c']
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources}
    assert digest(ROOT/'Lion King, The (World).md')=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    inputs=json.loads((ROOT/'build/md-next-levels-replay/frames.json').read_text())
    contract=json.loads((ROOT/'build/pride-death-timeline/report.json').read_text());death=contract['md_deaths'][0]['death']
    assert death==4755
    game=MdLab();sat=(C.c_ubyte*0x400).in_dll(game.core,'sat');satb=C.c_uint16.in_dll(game.core,'satb')
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    word=lambda p:game.work_ram[p&65535]|game.work_ram[(p+1)&65535]<<8
    rows=[];checks=0;pictures={0,1,2,24,25,225,226,268,270,273,291,298,305,345,346}
    try:
        with (out/'sat.bin').open('wb') as f:
            f.write(b'MDOSAT01')
            for frame in range(1,5401):
                game.step(inputs[frame-1]['pad'] if frame<=4000 else 0)
                if frame<=4000 and frame%100==1:
                    control=ROOT/f'build/md-next-levels-replay/{frame:05d}-wram.bin'
                    if control.exists():assert bytes(game.work_ram)==control.read_bytes();checks+=1
                age=frame-death
                if 0<=age<=360:
                    vram=bytes(game.vram);cache=bytes(sat);base=satb.value
                    assert base==((game.reg[5]&(0x7e if game.reg[12]&1 else 0x7f))<<9)
                    sprites=[];index=0;visited=set()
                    # The original core reads Y/size/link from its internal SAT
                    # cache, and name/attribute/X from VRAM, as vdp_render.c does.
                    for _ in range(80 if game.reg[12]&1 else 64):
                        assert index not in visited;visited.add(index)
                        y,link_size=struct.unpack_from('<HH',cache,index*8)
                        attr,x=struct.unpack_from('<HH',vram,base+index*8+4)
                        size=(link_size>>8)&15;w=8*(((size>>2)&3)+1);h=8*((size&3)+1)
                        sx=(x&511)-128;sy=(y&511)-128
                        sprites.append(dict(index=index,x=sx,y=sy,width=w,height=h,attr=attr,
                            palette=(attr>>13)&3,priority=(attr>>15)&1,
                            intersects_view=sx+w>0 and sx<320 and sy+h>0 and sy<224))
                        index=link_size&127
                        if not index:break
                    hero=word(0xcd48)
                    rows.append(dict(frame=frame,age=age,sat_base=base,linked=len(sprites),
                        intersects_view=sum(s['intersects_view'] for s in sprites),sprites=sprites,
                        health=word(0xccf6),lives=word(0xccee),hero=[word(hero+8),word(hero+10)],
                        camera=[word(0x880c),word(0x880e)],sat_cache_sha256=hashlib.sha256(cache).hexdigest(),
                        sat_vram_sha256=hashlib.sha256(vram[base:base+0x400]).hexdigest()))
                    f.write(struct.pack('<III',frame,age,base)+bytes(game.reg)+bytes(game.cram)+cache+vram)
                    if age in pictures:png(out/f'age-{age}.png',*game.image)
                if frame in (4800,5400):
                    assert bytes(game.work_ram)==(ROOT/f'build/pride-health-death-original/{frame}-wram.bin').read_bytes()
                game.samples.clear()
    finally:game.close()
    assert len(rows)==361 and checks==40
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    (out/'fields.json').write_text(json.dumps(rows,indent=2)+'\n')
    report.write_text(json.dumps(dict(result='PASS',scope=__doc__,fields=len(rows),prefix_full_ram_checks=checks,
        exact_original_full_ram_controls=[4800,5400],loaded_states=False,guest_edits=False,source_sha256=identities,
        artifacts_sha256={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p!=report}),indent=2)+'\n')
    print('Original MD SAT/cache/VRAM361 death/revival fields,40 prefix and two full RAM controls PASS',flush=True)


if __name__=='__main__':main()
