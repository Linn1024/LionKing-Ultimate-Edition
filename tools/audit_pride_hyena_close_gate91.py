"""Compare the original close-action gates after the earlier pounce branch."""
from pathlib import Path
verifier_source=Path(__file__).with_name('audit_pride_hyena_jump_gate89.py')
source=verifier_source.read_text()
start=source.index('    def md_gate(');end=source.index('    deltas=',start)
source=source[:start]+'''    def md_gate(dx,absdy,tag,facing):
        word(0xfaf2,absdy);word(0xfaf6,tag);word(0xfaf8,facing);word(0xfafc,dx)
        cpu.cycles=cpu.refresh=cpu.end=0;game.core.m68k_pulse_reset()
        for reg in range(16):game.core.m68k_set_reg(reg,0)
        for reg,value in [(17,0x2700),(14,0xfffb00),(15,0xfffd00),(16,0x19b0e2)]:game.core.m68k_set_reg(reg,value)
        for n in range(512):
            pc=game.core.m68k_get_reg(16)&0xffffff;assert cpu.pc&0xffffff==pc
            if pc in (0x19b114,0x19b152,0x19b15e):break
            game.core.m68k_run(cpu.cycles+1)
        else:raise AssertionError(('original MD close gate timeout',hex(pc)))
        assert game.core.m68k_get_reg(15)==0xfffd00
        return [1 if pc==0x19b114 else 2 if pc==0x19b152 else 0,0,0]
''' +source[end:]
changes=[
    ("reference=ROOT/'build/pride-enemy-motion88/report.json'","reference=ROOT/'build/pride-hyena-primary-gate90/report.json'"),
    ("assert r['result']=='SHARED_ENEMY_MOTION_VERIFIED'","assert r['result']=='PRIMARY_RESPONSE_JUMP_GATES_VERIFIED'"),
    ("ROOT/'build/pride-hyena-jump-gate89'","ROOT/'build/pride-hyena-close-gate91'"),
    ('pride_hyena_jump_gate89.c','pride_hyena_close_gate91.c'),
    ('native.hyena_jump_gate89','native.hyena_close_gate91'),
    ('argtypes=[C.c_int,C.c_int32,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]','argtypes=[C.c_int,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]'),
    ('deltas=list(range(-128,129))+[-2048,-512,512,2048]','deltas=list(range(-256,257))'),
    ('velocities=[-0x80000,-0x30001,-0x30000,-0x2ffff,-1,0,0x80000]','verticals=[0,1,29,30,31,100,512]'),
    ('for dx,vy,facing,cycle in itertools.product(deltas,velocities,(0,1,2,65535),(0,1,2,65535)):',
     'for dx,absdy,tag,facing in itertools.product(deltas,verticals,(0,1,2,3,65535),(0,1,2,65535)):'),
    ('native.hyena_close_gate91(dx,vy,facing,cycle,raw)','native.hyena_close_gate91(dx,absdy,tag,facing,raw)'),
    ('other=md_gate(dx,vy,facing,cycle)','other=md_gate(dx,absdy,tag,facing)'),
    ('row=dict(dx=dx,player_vy=vy,facing=facing,cycle=cycle','row=dict(dx=dx,absdy=absdy,tag=tag,facing=facing'),
    ('count==len(deltas)*len(velocities)*16','count==len(deltas)*len(verticals)*20'),
    ("result='STANDING_JUMP_GATE_VERIFIED'","result='CLOSE_ACTION_GATES_VERIFIED'"),
    ("native_slice=['C13DE3','C13E30','C13E90','C13EA0']","native_slice=['C13FA3','C13FC2','C13FF0','C13FFC']"),
    ("md_slice=['19AF16','19AF60','19AFBC','19AFCE']","md_slice=['19B0E2','19B114','19B152','19B15E']"),
    ('Cached standing-jump decision after earlier AI/contact/distance guards.','Cached close-action gates after earlier contact/distance/pounce decisions; selected calls C141C6/19B3A8.'),
    ('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,'),
]
for before,after in changes:
    assert source.count(before)==(2 if before=='native.hyena_jump_gate89' else 1),before
    source=source.replace(before,after)
source=source.replace('hops','responses')
exec(compile(source,str(verifier_source),'exec'))
