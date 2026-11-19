"""Capture original default-revival SAT/VRAM without guest edits or loaded states."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-default-actor/original-sat';out.mkdir(exist_ok=True)
    reference=ROOT/'build/pride-default-death-reference';contract=json.loads((reference/'report.json').read_text())
    assert contract['result']=='PASS';prefix=contract['selected_prefix_fields'];death=contract['case']['death']
    assert prefix==1400 and death==2902
    source=ROOT/'build/md-next-levels-replay';inputs=json.loads((source/'frames.json').read_text())
    expected={r['frame']:r for r in json.loads((reference/f'{prefix}/fields.json').read_text())}
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in
        (Path(__file__),ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md',
         ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'.tools/genesis-plus-gx/core/vdp_render.c',
         reference/'report.json',reference/f'{prefix}/fields.json',source/'frames.json')}
    results={};rows=[]
    for label in ('baseline','capture'):
        game=MdLab();sat=(C.c_ubyte*0x400).in_dll(game.core,'sat');satb=C.c_uint16.in_dll(game.core,'satb')
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        word=lambda p:game.work_ram[p&65535]|game.work_ram[(p+1)&65535]<<8
        file=(out/'sat.bin').open('wb') if label=='capture' else None
        if file:file.write(b'MDOSAT01')
        checks=0;observed=0
        try:
            for frame in range(1,death+321):
                game.step(inputs[frame-1]['pad'] if frame<=prefix else 0)
                if frame<=prefix and frame%100==1:
                    old=source/f'{frame:05d}-wram.bin'
                    if old.exists():assert bytes(game.work_ram)==old.read_bytes();checks+=1
                age=frame-death
                if frame in expected:
                    old=expected[frame];hero=word(0xcd48);draw=word(hero+12)
                    assert old['health']==word(0xccf6) and old['lives']==word(0xccee)
                    assert old['xy']==[word(hero+8),word(hero+10)] and old['camera']==[word(0x880c),word(0x880e)]
                    assert old['pose']==((word(draw+10)<<16|word(draw+12))&0xffffff)
                    assert old['cram']==bytes(game.cram).hex();observed+=1
                if frame==death+300:
                    image=out/(label+'-ready.png');png(image,*game.image)
                    assert digest(image)==digest(reference/f'{prefix}/revived.png')
                if file and 0<=age<=320:
                    vram=bytes(game.vram);cache=bytes(sat);base=satb.value
                    assert base==((game.reg[5]&(0x7e if game.reg[12]&1 else 0x7f))<<9)
                    sprites=[];index=0;visited=set()
                    for _ in range(80 if game.reg[12]&1 else 64):
                        assert index not in visited;visited.add(index)
                        y,link_size=struct.unpack_from('<HH',cache,index*8)
                        attr,x=struct.unpack_from('<HH',vram,base+index*8+4);size=(link_size>>8)&15
                        sprites.append(dict(index=index,x=(x&511)-128,y=(y&511)-128,
                            width=8*(((size>>2)&3)+1),height=8*((size&3)+1),attr=attr))
                        index=link_size&127
                        if not index:break
                    hero=word(0xcd48);draw=word(hero+12)
                    rows.append(dict(frame=frame,age=age,sprites=sprites,hero=[word(hero+8),word(hero+10)],
                        camera=[word(0x880c),word(0x880e)],pose=(word(draw+10)<<16|word(draw+12))&0xffffff,
                        timer=word(hero+26)>>8,health=word(0xccf6)))
                    file.write(struct.pack('<III',frame,age,base)+bytes(game.reg)+bytes(game.cram)+cache+vram)
                    if age in (0,1,24,274,277,295,300,302,307,320):png(out/f'age-{age}.png',*game.image)
                game.samples.clear()
            state=bytes(game.work_ram);(out/(label+'-final-wram.bin')).write_bytes(state)
            results[label]=dict(full_wram_sha256=hashlib.sha256(state).hexdigest(),prefix_controls=checks,existing_reference_fields=observed)
        finally:
            if file:file.close()
            game.close()
    assert results['baseline']==results['capture'] and len(rows)==321
    assert results['capture']['prefix_controls']==14 and results['capture']['existing_reference_fields']==301
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    (out/'fields.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,runs=results,fields=len(rows),
        loaded_states=False,guest_edits=False,source_sha256=identities,
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False),indent=2)+'\n')
    print('Original default SAT321 fields; 14 prefix/301 reference controls and full baseline RAM exact',flush=True)


if __name__=='__main__':main()
