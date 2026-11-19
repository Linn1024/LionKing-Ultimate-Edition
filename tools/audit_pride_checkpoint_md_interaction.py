"""Read-only original MD checkpoint pose usage on an ordinary power-on route.

Run with .tools/python32/python.exe. No task/state/ROM/code writes. CPU pose
usage is separate from displayed SAT/VRAM pixels and cross-version timing.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-checkpoint-player/original-md-interaction'
    out.mkdir(exist_ok=True)
    report_path=out/'report.json'
    report_path.write_text('{"result":"RUNNING"}\n')
    controls=ROOT/'build/md-next-levels-replay/frames.json'
    inputs=json.loads(controls.read_text())
    core=ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'
    rom=ROOT/'Lion King, The (World).md'
    assert digest(core)=='a6c45bbaf55010698fac6b8f0289428b54dc57dbdea12188472255358dea028a'
    assert digest(rom)=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    game=MdLab()
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513)
    game.core.retro_set_controller_port_device(1,513)
    observations=[]
    controls_checked=[]
    first={}
    try:
        for frame in range(1,4001):
            game.step(inputs[frame-1]['pad'])
            ram=bytes(game.work_ram)
            if frame%100==1:
                control=ROOT/f'build/md-next-levels-replay/{frame:05d}-wram.bin'
                if control.exists():
                    assert ram==control.read_bytes(),frame
                    controls_checked.append(control)
            if frame>=1000:
                for pose in (0x973b6,0x977c6,0x977fe):
                    pattern=struct.pack('<H',pose&65535)
                    offset=0x8000
                    while True:
                        offset=ram.find(pattern,offset)
                        if offset<0:break
                        draw=offset-12
                        offset+=1
                        if draw&1 or draw<0x8000 or draw>0xffe8 or ram[draw+10] != pose>>16:continue
                        position=struct.unpack_from('<H',ram,draw+4)[0]
                        if not 0x8008 <= position <= 0xff88:continue
                        task=position-8
                        if struct.unpack_from('<H',ram,task+12)[0] != draw:continue
                        observations.append(dict(frame=frame,pose=pose,draw=draw,
                            draw_words=list(struct.unpack_from('<12H',ram,draw)),position_word=position,task=task,
                            xy=list(struct.unpack_from('<HH',ram,position)),
                            descriptor_words=list(struct.unpack_from('<HH',ram,task+4)),
                            checkpoint=list(struct.unpack_from('<HH',ram,0xccd6))))
                        if pose not in first:
                            first[pose]=frame
                            (out/f'{frame}-wram.bin').write_bytes(ram)
                            png(out/f'{frame}.png',*game.image)
            game.samples.clear()
    finally:
        game.close()
    assert set(first)=={0x973b6,0x977c6,0x977fe},first
    (out/'raw-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
    rows=[r for r in observations if r['pose']!=0x973b6]
    assert rows and all(r['xy'] in ([656,592],[1200,112]) for r in rows)
    sources=[Path(__file__),ROOT/'tools/md_lab.py',controls,core,rom,*controls_checked]
    artifacts=[p for p in out.iterdir() if p.suffix in ('.png','.bin')]
    report=dict(result='AUDITED',scope=__doc__,ordinary_power_on=True,guest_or_rom_edits=False,
        original_pose_values_observed=first,observations=observations,
        original_prefix_control_snapshots=len(controls_checked),
        physical_sat_or_final_pixel_equivalence_verified=False,
        cross_version_animation_timing_equivalence_verified=False,
        full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        artifacts_sha256={p.name:digest(p) for p in artifacts})
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD checkpoint CPU poses observed: '+str(first)+'; displayed/timing comparison remains separate',flush=True)


if __name__=='__main__':
    main()
