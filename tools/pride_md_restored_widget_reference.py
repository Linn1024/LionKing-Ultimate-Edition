"""Read original MD HUD counters throughout ordinary health death/revival.

Embedded32-bit Python; power-on and controller-only. No state, CPU, ROM or actor
writes. Counter values and uploaded widget appearance are separate evidence.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-checkpoint-player/md-restored-widget-counters';out.mkdir(exist_ok=True)
    inputs_path=ROOT/'build/md-next-levels-replay/frames.json'
    inputs=json.loads(inputs_path.read_text())
    core=ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll';rom=ROOT/'Lion King, The (World).md'
    assert digest(core)=='a6c45bbaf55010698fac6b8f0289428b54dc57dbdea12188472255358dea028a'
    assert digest(rom)=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    word=lambda a:struct.unpack_from('<H',bytes(game.work_ram),a)[0]
    rows=[];controls=[]
    try:
        for frame in range(1,5401):
            game.step(inputs[frame-1]['pad'] if frame<=4000 else 0)
            if frame<=4000 and frame%100==1:
                control=ROOT/f'build/md-next-levels-replay/{frame:05d}-wram.bin'
                if control.exists():
                    assert bytes(game.work_ram)==control.read_bytes(),frame
                    controls.append(control)
            if frame in (4800,5400):
                control=ROOT/f'build/pride-health-death-original/{frame}-wram.bin'
                assert bytes(game.work_ram)==control.read_bytes(),frame
                controls.append(control)
            age=frame-4755
            if -1<=age<=645:
                rows.append(dict(frame=frame,age=age,health=word(0xccf6),health_max=word(0xccf8),
                    roar=word(0xccf2),roar_max=word(0xccf0),lives=word(0xccee),
                    checkpoint=[word(0xccd6),word(0xccd8)]))
            game.samples.clear()
    finally:game.close()
    assert len(rows)==647 and len(controls)==42
    sources=[Path(__file__),ROOT/'tools/md_lab.py',inputs_path,core,rom,*controls]
    result=dict(result='PASS',scope=__doc__,ordinary_power_on=True,guest_edits=False,loaded_states=False,
        original_full_ram_controls=len(controls),fields=rows,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    samples=[r for r in rows if r['age'] in (269,270,271,273,300,345,346,347,360,400,645)]
    print('Original MD revival counters: '+json.dumps(samples),flush=True)


if __name__=='__main__':main()
