"""Check the original roar recharge predicate at equal clock/counter inputs.

Embedded32-bit Python. Original MD instruction slice executes in isolated RAM
fixtures, with interrupts masked; these are not ordinary gameplay captures.
The original native slice has the same AND31/conditional INC16 instruction rule.
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
    out=ROOT/'build/pride-revival-roar-clock';out.mkdir(exist_ok=True)
    md_path=ROOT/'Lion King, The (World).md';snes_path=ROOT/'Lion King, The (USA).sfc'
    md=md_path.read_bytes();snes=snes_path.read_bytes()
    assert digest(md_path)=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    assert digest(snes_path)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert snes[0xb54a:0xb555]==bytes.fromhex('ad0a0a291f00d003ee0220')
    code=md[0x7ddce:0x7dde0]
    assert code==bytes.fromhex('2039ffff81be0200001f66065279ffffccf2')
    game=MdLab();game.write_code(0xfe00,code+bytes.fromhex('60fe'))
    def word(at,value):
        game.work_ram[at]=value&255;game.work_ram[at+1]=value>>8&255
    clocks=list(range(256))+[0xffff,0x10000,0x10020,0x12345660,0x1234567f,0xffffffff]
    checked=0;increments=0
    try:
        for clock in clocks:
            for value in (0,1,23,24,65535):
                word(0x81be,clock>>16);word(0x81c0,clock&65535);word(0xccf2,value)
                game.core.m68k_set_reg(17,0x2700)
                game.core.m68k_set_reg(15,0xfffd00)
                game.core.m68k_set_reg(16,0xfffe00)
                game.step()
                actual=game.work_ram[0xccf2]|game.work_ram[0xccf3]<<8
                expected=(value+1)&65535 if clock&31==0 else value
                assert actual==expected,(clock,value,actual,expected)
                checked+=1;increments+=clock&31==0
                game.samples.clear()
    finally:game.close()
    sources=[Path(__file__),ROOT/'tools/md_lab.py',md_path,snes_path,
             ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    result=dict(result='PASS',scope=__doc__,original_md_instruction_fixtures=checked,
        increment_fixtures=increments,native_original_instruction_rule='INC16(counter) iff (word[$0A0A] & 31) == 0',
        md_original_instruction_rule='ADDQ.W #1,counter iff (long[$81BE] & 31) == 0',
        equal_low_clock_phase_rule_verified=True,native_original_cpu_execution=False,
        ordinary_gameplay=False,guest_value_and_code_fixtures=True,rom_patched=False,
        absolute_cross_version_clock_phase_equivalence=False,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(str(checked)+' original MD clock/counter cases; native instruction rule agrees at equal low clock phase. Absolute phase remains separate',flush=True)


if __name__=='__main__':main()
