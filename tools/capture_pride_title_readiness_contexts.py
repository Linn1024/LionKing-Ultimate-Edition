"""Observe original MD title presentation and input boundaries after real final exits."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def picture(game):
    data,w,h,pitch,fmt=game.image;assert (w,h,fmt)==(320,224,2)
    return hashlib.sha256(b''.join(data[y*pitch:y*pitch+640] for y in range(224))).hexdigest()

def main():
    out=ROOT/'build/pride-title-readiness-original';out.mkdir();checks={};cases={}
    references=[ROOT/'build/pride-game-over-exits-original/report.json',ROOT/'build/pride-final-input-reference/report.json',
                ROOT/'build/pride-game-over-title-boundary-original/report.json',ROOT/'build/pride-final-title-phases/report.json']
    for path in references:bound(path)
    pads=ROOT/'build/pride-final-arena-original/inputs.json';fatal_pad=json.loads(pads.read_text())[4598-1]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    game.core.retro_serialize_size.restype=C.c_size_t
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    scenarios=[('game-over-timeout',True,None,370,515),('game-over-button',True,140,186,331),
               ('continue-no',False,140,186,331),('continue-timeout',False,None,890,1035)]
    try:
        for name,go,decision,first,estimate in scenarios:
            folder=out/name;folder.mkdir();state=references[0].parent/'prefatal.state' if go else references[1].parent/'prefatal.state'
            raw=state.read_bytes();blob=C.create_string_buffer(raw);assert game.core.retro_unserialize(blob,len(raw))
            checkpoint=None;rows=[];neutral={};end=estimate+100
            for age in range(end+1):
                pad=(fatal_pad if go else 128) if age==0 else 0
                if decision is not None:
                    if not go and 130<=age<=133:pad=128
                    if decision<=age<=decision+3:pad=256
                game.step(pad);game.samples.clear()
                if age==estimate-32:
                    n=game.core.retro_serialize_size();checkpoint=C.create_string_buffer(n);assert game.core.retro_serialize(checkpoint,n)
                    (folder/'before-input.state').write_bytes(checkpoint.raw)
                if age>=first-5:
                    sha=picture(game);neutral[age]=sha
                    rows.append(dict(age=age,picture_sha256=sha,cram=bytes(game.cram).hex(),registers=list(game.reg)))
                if age in (first,first+1,first+10,first+30,first+60,first+100,estimate-1,estimate,estimate+30):
                    png(folder/f'{age}.png',*game.image)
                    (folder/f'{age}-vram.bin').write_bytes(bytes(game.vram));(folder/f'{age}-cram.bin').write_bytes(bytes(game.cram))
            probes=[]
            plans=[(f'start{at}',at,at,8) for at in range(estimate-8,estimate+9)]
            plans += [('held-through-ready',estimate-20,estimate+1,8),('released-before-ready',estimate-20,estimate-1,8)]
            plans += [(f'{label}{at}',at,at,button) for label,button in [('a',256),('b',1),('c',2),('up',16),('down',32)] for at in (estimate-1,estimate)]
            for label,pressed,release,button in plans:
                assert game.core.retro_unserialize(checkpoint,n);first_diff=None
                for age in range(estimate-31,end+1):
                    game.step(button if pressed<=age<=release else 0);game.samples.clear()
                    if first_diff is None and picture(game)!=neutral[age]:first_diff=age
                probes.append(dict(label=label,pressed=pressed,released=release,button=button,first_picture_change=first_diff,end_picture_sha256=picture(game)))
                if label in (f'start{estimate-1}',f'start{estimate}','held-through-ready','released-before-ready',f'down{estimate}'):
                    png(folder/f'{label}-end.png',*game.image)
            accepted=[r['pressed'] for r in probes if r['button']==8 and r['pressed']==r['released'] and r['first_picture_change'] is not None]
            actual=min(accepted);checks[name+'_single_boundary']=actual==estimate and all((r['first_picture_change'] is not None)==(r['pressed']>=actual)
                for r in probes if r['button']==8 and r['pressed']==r['released'])
            checks[name+'_held_into_ready']=next(r for r in probes if r['label']=='held-through-ready')['first_picture_change'] is not None
            checks[name+'_released_before_ready_ignored']=next(r for r in probes if r['label']=='released-before-ready')['first_picture_change'] is None
            # Follow a genuine accepted Start long enough to inspect gameplay.
            assert game.core.retro_unserialize(checkpoint,n)
            for age in range(estimate-31,estimate+601):game.step(8 if age==actual else 0);game.samples.clear()
            png(folder/'accepted-gameplay.png',*game.image)
            cases[name]=dict(first_title=first,first_start=actual,relative_to_first_picture=actual-first,frames=rows,probes=probes)
            print(name,'firstStart',actual,'relative',actual-first,flush=True)
    finally:game.close()
    paths=[Path(__file__),pads,*references,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,ordinary_routes=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True);assert all(checks.values())

if __name__=='__main__':main()
