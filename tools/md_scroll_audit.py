"""Disassemble MD background descriptor callbacks for local research.

Requires Capstone (normal Python package or .tools/pythonlibs).
Linear scan to the first RTS is evidence, not complete control-flow analysis.
"""
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.tools/pythonlibs'))
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from audit_scenes import ROOT,read_rom

def main():
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    lines=[]
    for level in range(14):
        desc=struct.unpack_from('>I',rom,0x1cfdb4+level*48+32)[0]
        for role,fn in zip(('update','initialize'),struct.unpack_from('>II',rom,desc)):
            lines.append(f'\nLEVEL {level} {role} {fn:06x} (linear scan to first RTS; not a control-flow proof)')
            for i in md.disasm(rom[fn:fn+8192],fn):
                lines.append(f'{i.address:06x}  {i.mnemonic:12} {i.op_str}')
                if i.mnemonic=='rts': break
    dest=ROOT/'build/scene-audit/md-routines.txt'; dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text('\n'.join(lines)+'\n'); print(dest,len(lines),'lines')

if __name__=='__main__': main()
