"""Evaluate both originals' bounded ledge-tag branches for every byte tag.

This evaluates decoded original comparisons/branches, not whole CPU routines.
Actor movement, animation choices and all nonledge branches remain separate.
"""
import json
from pathlib import Path
import re
import sys

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
sys.path.insert(0,str(ROOT/'engine/snesrecomp'))
sys.path.insert(0,str(ROOT/'.tools/pythonlibs'))
from recompiler.snes65816 import decode_insn
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000


def native_target(rom,start,end,tag):
    pc=start;negative=zero=False
    for _ in range(100):
        if pc>=end:return None
        ins=decode_insn(rom,pc&0x3fffff,pc&65535,pc>>16,0,0);assert ins
        target=pc+ins.length
        if ins.mnem=='LDA':assert ins.operand==7 and rom[pc&0x3fffff]==0xa3
        elif ins.mnem=='CMP':
            assert rom[pc&0x3fffff]==0xc9
            result=(tag-ins.operand)&65535;negative=bool(result&32768);zero=result==0
        elif ins.mnem in ('BMI','BPL','BEQ','BNE'):
            take={'BMI':negative,'BPL':not negative,'BEQ':zero,'BNE':not zero}[ins.mnem]
            if take:target=0xc30000|ins.operand
        elif ins.mnem=='PEI':pass
        elif ins.mnem=='JSL':return ins.operand
        else:raise AssertionError((hex(pc),ins.mnem))
        pc=target
    raise AssertionError('Native tag branch did not terminate')


def md_target(rom,start,end,tag):
    cpu=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions={ins.address:ins for ins in cpu.disasm(rom[start:end],start)}
    pc=start;comparison=0
    for _ in range(100):
        if pc>=end:return None
        ins=instructions[pc];target=pc+ins.size
        if ins.mnemonic=='cmpi.w':
            match=re.fullmatch(r'#\$([0-9a-f]+), \$8\(a6\)',ins.op_str);assert match,ins.op_str
            comparison=tag-int(match[1],16)
        elif ins.mnemonic in ('blt.w','bgt.w','bne.w'):
            take={'blt.w':comparison<0,'bgt.w':comparison>0,'bne.w':comparison!=0}[ins.mnemonic]
            if take:target=int(ins.op_str.removeprefix('$'),16)
        elif ins.mnemonic in ('move.w','move.l'):pass
        elif ins.mnemonic=='jsr':return int(ins.op_str.removesuffix('.l').removeprefix('$'),16)
        else:raise AssertionError((hex(pc),ins.mnemonic,ins.op_str))
        pc=target
    raise AssertionError('MD tag branch did not terminate')


def main():
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    out=ROOT/'build/pride-ledge-tags';out.mkdir();directions={}
    for name,ns,ne,nt,ms,me,mt in (
        ('left',0xc3520c,0xc352b2,0xc33d1f,0x19600e,0x1960f4,0x194b94),
        ('right',0xc353de,0xc35484,0xc33f11,0x19623e,0x196324,0x194da6)):
        accepted=[]
        for tag in range(256):
            a=native_target(snes,ns,ne,tag);b=md_target(md,ms,me,tag)
            assert a in (None,nt) and b in (None,mt)
            assert (a is not None)==(b is not None),(name,tag,a,b)
            if a is not None:accepted.append(tag)
        expected=[*range(0x8c,0x90),*range(0x9c,0xa0),*range(0xea,0xef),*range(0xfb,0xff)]
        assert accepted==expected
        directions[name]=dict(accepted_tags=accepted,native_branch=[hex(ns),hex(ne)],md_branch=[hex(ms),hex(me)],
            native_constructor=hex(nt),md_constructor=hex(mt))
    paths=[Path(__file__),ROOT/'tools/snes_disassemble.py',ROOT/'tools/md_disassemble.py']
    report=dict(result='ORIGINAL_LEDGE_TAG_BRANCHES_MATCH',evaluated_byte_tags_per_direction=256,
        direction_tag_comparisons=512,directions=directions,full_cpu_or_lifetime_equivalence_proven=False,
        production_mapping_enabled=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'512 comparisons;17 matching ledge tags per direction',flush=True)


if __name__=='__main__':main()
