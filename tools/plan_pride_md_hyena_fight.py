"""Author ordinary MD hyena-fight inputs with complete reference checkpoints.

Checkpoints branch controller choices only. Selected inputs are replayed from
power-on, and complete reference state must match the planned result.
"""
import argparse
import ctypes as C
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT, MdLab, png
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--difficulty',choices=('normal','hard'),default='normal')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--rounds',type=int,default=28)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    base=ROOT/'build/pride-hyena-hits/md';report=base/'report.json';bound(report)
    source=base/args.difficulty/'inputs.json';prefix=json.loads(source.read_text())[:4100]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_serialize_size.restype=C.c_size_t
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    def snapshot():
        size=game.core.retro_serialize_size();buf=C.create_string_buffer(size)
        assert game.core.retro_serialize(buf,size)
        assert b'TLKAE001' in buf.raw
        return buf.raw
    def restore(raw):
        buf=C.create_string_buffer(raw);assert game.core.retro_unserialize(buf,len(raw))
        game.samples.clear()
    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
    actor=int(json.loads((base/args.difficulty/'frames.json').read_text())[0]['actor'])
    def info():
        return dict(level=word(0xccce),lives=word(0xccee),health=word(0xccf6),
            x=word(0x93ce+8),y=word(0x93ce+10),boss_health=word(actor+0x2a),
            boss_cycle=word(actor+0x28),boss_x=word(actor+8),boss_action=word(actor+0x30)<<16|word(actor+0x32))
    def step(pad):game.step(pad);game.samples.clear()
    L,R,J=64,128,256;size=40
    patterns={'wait':[0]*size,'L':[L]*size,'R':[R]*size,'J':[J]*12+[0]*28,
        'LJ':[L]*2+[L|J]*12+[L]*26,'RJ':[R]*2+[R|J]*12+[R]*26,
        'LJR':[L]*2+[L|J]*12+[R]*26,'RJL':[R]*2+[R|J]*12+[L]*26,
        'runLJ':[L]*12+[L|J]*12+[L]*16,'runRJ':[R]*12+[R|J]*12+[R]*16,
        'JL':[J]*12+[L]*28,'JR':[J]*12+[R]*28}
    try:
        for pad in prefix:step(pad)
        initial=info();beam=[dict(state=snapshot(),info=initial,pads=[],actions=[])]
        history=[];best=beam[0]
        for depth in range(1,args.rounds+1):
            nodes=[]
            for parent in beam:
                for name,pads in patterns.items():
                    restore(parent['state'])
                    for pad in pads:step(pad)
                    observed=info()
                    if observed['level']!=1 or observed['lives']<initial['lives'] or not observed['health']:continue
                    if observed['boss_health']>initial['boss_health']:continue
                    nodes.append(dict(state=snapshot(),info=observed,pads=parent['pads']+pads,actions=parent['actions']+[name]))
            if not nodes:break
            def score(n):
                v=n['info']
                return v['boss_health']*1000+(initial['health']-v['health'])*25+abs(v['x']-v['boss_x'])*.04-(35 if v['boss_action']==0x19b7ba else 0)
            nodes.sort(key=score);beam=[];bins=set()
            for node in nodes:
                v=node['info'];key=(v['x']//24,v['y']//16,v['boss_action'],v['boss_health'])
                if key in bins:continue
                bins.add(key);beam.append(node)
                if len(beam)==3:break
            best=beam[0];history.append(dict(depth=depth,info=best['info'],actions=best['actions']))
            print('MD depth',depth,best['info'],flush=True)
            if best['info']['boss_health']==0:break
        selected=prefix+best['pads'];(out/'selected-inputs.json').write_text(json.dumps(selected)+'\n')
        expected=best['state'];game.close()
        game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        game.core.retro_serialize_size.restype=C.c_size_t
        game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
        for pad in selected:step(pad)
        actual=snapshot();assert actual==expected,'Uninterrupted reference state differs from planning'
        png(out/'uninterrupted.png',*game.image)
        (out/'uninterrupted.state').write_bytes(actual)
        paths=[Path(__file__),ROOT/'tools/md_lab.py',report,source,ROOT/'Lion King, The (World).md',
               ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
        result=dict(result='AUTHORED' if best['info']['boss_health']==0 else 'PARTIAL',scope=__doc__,
            initial=initial,final=info(),history=history,frames=len(selected),
            uninterrupted_complete_state_matches_planning=True,game_or_rom_edits=False,
            source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
            artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
        (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    finally:game.close()


if __name__=='__main__':main()
