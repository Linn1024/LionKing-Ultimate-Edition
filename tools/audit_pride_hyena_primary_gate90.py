"""Original close-player voice-action and standing-jump gates at matched inputs."""
from pathlib import Path
verifier_source=Path(__file__).with_name('audit_pride_hyena_jump_gate89.py')
source=verifier_source.read_text()
changes=[
    ("reference=ROOT/'build/pride-enemy-motion88/report.json'","reference=ROOT/'build/pride-hyena-jump-gate89/report.json'"),
    ("assert r['result']=='SHARED_ENEMY_MOTION_VERIFIED'","assert r['result']=='STANDING_JUMP_GATE_VERIFIED'"),
    ("ROOT/'build/pride-hyena-jump-gate89'","ROOT/'build/pride-hyena-primary-gate90'"),
    ('pride_hyena_jump_gate89.c','pride_hyena_primary_gate90.c'),
    ('native.hyena_jump_gate89','native.hyena_primary_gate90'),
    ('argtypes=[C.c_int,C.c_int32,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]','argtypes=[C.c_int,C.c_int,C.c_int32,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]'),
    ('def md_gate(dx,vy,facing,cycle):','def md_gate(dx,dy,vy,facing,cycle):\n        word(0xfafa,dy)'),
    ('(16,0x19af16)','(16,0x19aee0)'),
    ('pc in (0x19af60,0x19afbc,0x19afce)','pc in (0x19af0a,0x19af60,0x19afbc,0x19afce)'),
    ('choice=1 if pc==0x19af60 else 2 if pc==0x19afbc else 0','choice=3 if pc==0x19af0a else 1 if pc==0x19af60 else 2 if pc==0x19afbc else 0'),
    ('deltas=list(range(-128,129))+[-2048,-512,512,2048]','deltas=[-2048,-512,-101,-100,-99,-41,-40,-39,-1,0,1,39,40,41,99,100,101,512,2048]\n    verticals=[-513,-512,-33,-32,-31,0,32,512,513]'),
    ('velocities=[-0x80000,-0x30001,-0x30000,-0x2ffff,-1,0,0x80000]','velocities=[-0x80000,-0x30001,-0x30000,-0x2ffff,0,0xffff,0x10000,0x10001,0x80000]'),
    ('count=hops=0;failures=[]','count=hops=0;failures=[];outcomes=set()'),
    ('for dx,vy,facing,cycle in itertools.product(deltas,velocities,','for dx,dy,vy,facing,cycle in itertools.product(deltas,verticals,velocities,'),
    ('native.hyena_primary_gate90(dx,vy,facing,cycle,raw)','native.hyena_primary_gate90(dx,dy,vy,facing,cycle,raw)'),
    ('other=md_gate(dx,vy,facing,cycle)','other=md_gate(dx,dy,vy,facing,cycle)'),
    ('count+=1;hops+=bool(raw[0])','count+=1;hops+=bool(raw[0]);outcomes.add(int(raw[0]))'),
    ('row=dict(dx=dx,player_vy=vy','row=dict(dx=dx,dy=dy,player_vy=vy'),
    ('count==len(deltas)*len(velocities)*16','count==len(deltas)*len(verticals)*len(velocities)*16'),
    ('both_true_and_false_paths_observed=0<hops<count','all_four_outcomes_observed=outcomes=={0,1,2,3}'),
    ("result='STANDING_JUMP_GATE_VERIFIED'","result='PRIMARY_RESPONSE_JUMP_GATES_VERIFIED'"),
    ("native_slice=['C13DE3','C13E30','C13E90','C13EA0']","native_slice=['C13DA7','C13DD7','C13E30','C13E90','C13EA0']"),
    ("md_slice=['19AF16','19AF60','19AFBC','19AFCE']","md_slice=['19AEE0','19AF0A','19AF60','19AFBC','19AFCE']"),
    ('Cached standing-jump decision after earlier AI/contact/distance guards.','Cached close-player voice-action and standing-jump decisions after earlier contact/distance guards.'),
    ('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,'),
]
for before,after in changes:
    assert source.count(before)==(2 if before=='native.hyena_jump_gate89' else 1),before
    source=source.replace(before,after)
source=source.replace('if choice else','if choice in (1,2) else')
source=source.replace('selected_hops=hops','selected_actions=hops')
exec(compile(source,str(verifier_source),'exec'))
