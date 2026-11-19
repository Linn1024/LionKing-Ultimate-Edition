"""Disassemble a bounded local MD ROM range for research (output is not game code)."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/pythonlibs'))
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from pride_sprite_catalog import read_rom

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('start',type=lambda s:int(s,16));ap.add_argument('end',type=lambda s:int(s,16))
    args=ap.parse_args()
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    assert 0<=args.start<args.end<=len(rom)
    cpu=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    for instruction in cpu.disasm(rom[args.start:min(len(rom),args.end+16)],args.start):
        if instruction.address+instruction.size>args.end:break
        print(f'{instruction.address:06x} {instruction.mnemonic:12} {instruction.op_str}')

if __name__=='__main__':main()
