"""Compare walking/turn selection with complete original wall-query execution."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
verifier_source=Path(__file__).with_name('audit_pride_hyena_pounce_gate93.py')
source=verifier_source.read_text()
start=source.index('    def md_gate(');end=source.index('    boundaries=',start)
source=source[:start]+'''    C.memset(C.addressof(game.work_ram),0,65536)
    word(0xcd1e,16);longword(0xcd22,0xffe000);longword(0xcd2e,0xffe100)
    for at in range(0,128,2):word(0xe000+at,8)
    longword(0x81c4,0xff98ce);word(0x98ce+12,0x9b00)
    def md_gate(dx,terrain,tag,facing,ground,rng,y):
        word(0xfaec,ground);word(0xfaee,0);word(0xfaf6,tag);word(0xfaf8,facing);word(0xfafc,dx);word(0xfafe,rng)
        word(0x98ce+8,64);word(0x98ce+10,y);word(0x98ce+0x20,facing);word(0x98ce+0x2e,tag)
        word(0x98ce+0x40,terrain<<8);word(0x98ce+0x46,0)
        game.work_ram[(0x9b00+8)^1]=8 if facing else 0
        game.work_ram[0xe106^1]=terrain
        cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(14,0xfffb00),(15,0xfffd00),(16,0x19b15e)]:game.core.m68k_set_reg(reg,value)
        for n in range(4096):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc in (0x19b19a,0x19b1e8,0x19b37e):break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('original MD walk timeout',hex(pc)))
        choice=1 if pc==0x19b19a else 2 if pc==0x19b1e8 else 0
        sp=game.core.m68k_get_reg(15);assert sp==(0xfffcfe if choice else 0xfffd00)
        assert game.core.m68k_get_reg(14)==0xfffb00
        turn=word(0xfaee)
        if turn:assert longword(0x98ce+0xe)==0xb8842
        return [choice,turn,word(0x98ce+0x20),word(0x98ce+0x2e),int(bool(game.work_ram[(0x9b00+8)^1]&8)),word(0x98ce+0x46),word(sp) if choice else 0]
''' +source[end:]
start=source.index('    boundaries=');end=source.index('    count=0;',start)
source=source[:start]+'''    boundaries=[-21,-20,-1,0,1,20,21]
    grid=itertools.product(boundaries,range(256),(0,1),(0,1),(0,1),(0,1),(40,48))
    sweep=itertools.product((-21,0,21),(0,6,0x4e,0x4f,0x53,0x63,0x73,0xb3,0xc3,0xeb,0xec,0xed,0xee),(1,),(0,1),(0,1),(0,1,8,9),range(32,48))
''' +source[end:]
changes=[
    ("reference=ROOT/'build/pride-hyena-close-gate91/report.json'","reference=ROOT/'build/pride-hyena-pounce-gate93/report.json'"),
    ("'CLOSE_ACTION_GATES_VERIFIED'","'POUNCE_GATES_VERIFIED'"),
    ("out=ROOT/'build/pride-hyena-pounce-gate93'","out=ROOT/'build/pride-hyena-walk-gate94'"),
    ('pride_hyena_pounce_gate93.c','pride_hyena_walk_gate94.c'),
    ('native.hyena_pounce_gate93','native.hyena_walk_gate94'),
    ('argtypes=[C.c_int,C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]','argtypes=[C.POINTER(C.c_uint),C.POINTER(C.c_uint)]'),
    ('for dx,terrain,tag,facing,ground in itertools.chain(grid,sweep):','for dx,terrain,tag,facing,ground,rng,y in itertools.chain(grid,sweep):'),
    ('raw=(C.c_uint*3)();assert native.hyena_walk_gate94(dx,terrain,tag,facing,ground,raw),(dx,terrain,tag,facing,ground)',
     'raw=(C.c_uint*7)();args=(C.c_uint*7)(dx&65535,terrain,tag,facing,ground,rng,y);assert native.hyena_walk_gate94(args,raw),list(args)'),
    ('other=md_gate(dx,terrain,tag,facing,ground)','other=md_gate(dx,terrain,tag,facing,ground,rng,y)'),
    ('ground=ground,snes=list(raw)','ground=ground,rng=rng,y=y,snes=list(raw)'),
    ('expected=len(boundaries)*256*3*4*2+513*18*2','expected=len(boundaries)*256*2**6+3*13*2*2*4*16'),
    ("result='POUNCE_GATES_VERIFIED'","result='WALK_GATES_VERIFIED'"),
    ("['C13EA0','C13F10','C13F93','C13FA3']","['C13FFC','C14022','C14056','C141A0']"),
    ("['19AFCE','19B046','19B0D0','19B0E2']","['19B15E','19B19A','19B1E8','19B37E']"),
    ("['C19399','C19415','C193E1','C1371F']","['C0C801','C0C82B','C19415','C193E1','C194C8']"),
    ("['18E8E8','18E9F6','18E962','19A8AA']","['0023F4','00242E','18E9F6','18E962','18EBA0']"),
    ('Cached pounce decisions after earlier guards. Complete original terrain/orientation helper execution, no interception. Terrain byte0..255 with neighboring byte zero. Stops before selected action; no whole AI, action or collision proof.',
     'Walking/turn decisions after earlier action gates; complete original wall queries on uniform synthetic 8x8 tile map and orientation writes. Stops before retreat action or final movement/animation. No whole AI/scene trajectory proof.'),
    ('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,'),
]
for before,after in changes:
    assert source.count(before)==(2 if before=='native.hyena_pounce_gate93' else 1),before
    source=source.replace(before,after)
exec(compile(source,str(verifier_source),'exec'))
