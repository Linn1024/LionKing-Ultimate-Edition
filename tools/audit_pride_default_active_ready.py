"""Observe original MD ready-boundary Right input, with no states or guest edits."""
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
    out=ROOT/'build/pride-spawn-revival/original-active-ready';out.mkdir(exist_ok=True)
    source=ROOT/'build/md-next-levels-replay';frames=json.loads((source/'frames.json').read_text())
    reference=ROOT/'build/pride-default-death-reference/1400/fields.json'
    expected={r['frame']:r for r in json.loads(reference.read_text())}
    sat_reference=ROOT/'build/pride-default-actor/original-sat/sat.bin';neutral_sat=sat_reference.read_bytes()
    assert neutral_sat[:8]==b'MDOSAT01';record_size=66732;death=2902;prefix=1400
    controls={};runs={}
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),ROOT/'tools/md_lab.py',
        ROOT/'Lion King, The (World).md',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
        ROOT/'.tools/genesis-plus-gx/libretro/libretro-common/include/libretro.h',source/'frames.json',reference,sat_reference)}
    for label,onset in (('neutral',None),('right-299',299),('right-300',300),('right-301',301)):
        folder=out/label;folder.mkdir(exist_ok=True);game=MdLab();rows=[];prefix_checks=reference_checks=full_controls=0
        sat=(C.c_ubyte*0x400).in_dll(game.core,'sat');satb=C.c_uint16.in_dll(game.core,'satb')
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        def word(p):return game.work_ram[p&65535]|game.work_ram[(p+1)&65535]<<8
        def pointer(p):return ((word(p)<<16)|word(p+2))&0xffffff
        try:
            with (folder/'sat.bin').open('wb') as f:
                f.write(b'MDOSAT01')
                for frame in range(1,death+313):
                    age=frame-death;pad=frames[frame-1]['pad'] if frame<=prefix else 128 if onset is not None and age>=onset else 0
                    game.step(pad)
                    if frame<=prefix and frame%100==1:
                        p=source/f'{frame:05d}-wram.bin'
                        if p.exists():assert bytes(game.work_ram)==p.read_bytes();prefix_checks+=1
                    if frame in expected and (onset is None or age<onset):
                        old=expected[frame];hero=word(0xcd48);draw=word(hero+12)
                        assert (old['health'],old['lives'],old['xy'],old['camera'],old['pose'],old['cram'])==(
                            word(0xccf6),word(0xccee),[word(hero+8),word(hero+10)],[word(0x880c),word(0x880e)],pointer(draw+10),bytes(game.cram).hex())
                        reference_checks+=1
                    if 296<=age<=312:
                        state=bytes(game.work_ram)
                        if onset is None:controls[age]=state
                        elif age<onset:assert state==controls[age];full_controls+=1
                        hero=word(0xcd48);draw=word(hero+12);base=satb.value
                        raw=struct.pack('<III',frame,age,base)+bytes(game.reg)+bytes(game.cram)+bytes(sat)+bytes(game.vram)
                        assert len(raw)==record_size
                        if onset is None or age<onset:assert raw==neutral_sat[8+age*record_size:8+(age+1)*record_size]
                        f.write(raw)
                        rows.append(dict(frame=frame,age=age,pad=pad,xy=[word(hero+8),word(hero+10)],
                            pose=pointer(draw+10),callback=pointer(hero+14),cursor=pointer(hero+18),timer=word(hero+26)>>8,
                            state_word=word(hero+48),camera=[word(0x880c),word(0x880e)],health=word(0xccf6)))
                        if age in (299,300,301,302,305,312):
                            png(folder/f'age-{age}.png',*game.image);(folder/f'age-{age}-wram.bin').write_bytes(state)
                    game.samples.clear()
            assert prefix_checks==14 and len(rows)==17
            (folder/'fields.json').write_text(json.dumps(rows,indent=2)+'\n')
            runs[label]=dict(right_onset_age=onset,prefix_controls=prefix_checks,existing_cpu_reference_fields=reference_checks,
                full_pre_input_controls=full_controls,fields=len(rows),artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
            print(label,[(r['age'],r['xy'][0],hex(r['pose']),r['timer'],hex(r['callback'])) for r in rows if 299<=r['age']<=303],flush=True)
        finally:game.close()
    for name,sha in sources.items():assert digest(ROOT/name)==sha,name
    (out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_SOURCE_OBSERVED',scope=__doc__,runs=runs,
        source_sha256=sources,loaded_states=False,guest_edits=False,port_active_input_fidelity_verified=False,
        full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
