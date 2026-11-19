"""Linear bounded SNES ROM research listing; branch-dependent widths need review."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine/snesrecomp'))
from recompiler.snes65816 import decode_insn
from pride_sprite_catalog import read_rom

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('start',type=lambda s:int(s,16));ap.add_argument('end',type=lambda s:int(s,16))
    ap.add_argument('--m',type=int,default=0);ap.add_argument('--x',type=int,default=1)
    args=ap.parse_args();m,x=args.m,args.x;stack=[]
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    address=args.start
    while address<args.end:
        ins=decode_insn(rom,address&0x3fffff,address&65535,address>>16,m,x)
        if not ins:break
        print(f'{address:06x} {ins.mnem:4} {str(ins.mode):12} {ins.operand:06x}')
        if ins.mnem=='PHP':stack.append((m,x))
        elif ins.mnem=='PLP' and stack:m,x=stack.pop()
        elif ins.mnem=='SEP':m|=bool(ins.operand&32);x|=bool(ins.operand&16)
        elif ins.mnem=='REP':m&=not bool(ins.operand&32);x&=not bool(ins.operand&16)
        address+=ins.length

if __name__=='__main__':main()
