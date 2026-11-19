"""Author ordinary native repeated-hit controls, stopping at owned hyena death.

Complete checkpoints explore controller branches. The selected prefix is replayed
from power-on and its entire WRAM must match planning. Bonus slot reuse is excluded.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--difficulty',choices=('normal','hard'),default='hard')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--rounds',type=int,default=28)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    base=ROOT/'build/pride-hyena-hits/snes';capture=base/'report.json';bound(capture)
    tape=base/args.difficulty/'ordinary.polled.tape';profile=base/args.difficulty/'resources.ini'
    exe=ROOT/'engine/build-win/tlk_headless.exe'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    def run(label,frame,inputs,load=None):
        folder=out/label;folder.mkdir();input_path=folder/'input.polled.tape';input_path.write_bytes(inputs)
        command=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,
            '--input-polled',input_path,'--frames',frame,'--save-at',frame,folder/'end.state']
        if load:command.extend(['--load',load])
        local=dict(env,TLK_WRAM_DUMP=str(frame),TLK_WRAM_DIR=str(folder))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,command)),cwd=ROOT,env=local,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
        used=int(re.search(r'tape_words_used=(\d+)',(folder/'run.log').read_text()).group(1))
        ram=(folder/f'hl_wram_{frame}.bin').read_bytes();word=lambda a:struct.unpack_from('<H',ram,a)[0]
        actor=0xba13
        observed=dict(level=word(0x1ff9e),descriptor=word(0xdf),health=word(0x2004),lives=word(0x1ffaa),
            x=word(0xb21b),y=word(0xb21d),boss_x=word(actor+8),boss_health=word(actor+0x2a),
            boss_action=word(actor+0x30)|word(actor+0x32)<<16,boss_cycle=word(actor+0x28))
        return dict(folder=folder,frame=frame,info=observed,used=used,ram=ram)
    anchor=run('anchor',4000,tape.read_bytes());initial=anchor['info']
    assert initial['descriptor']==0x80d and 0<initial['boss_health']<=2
    anchor.update(prefix=tape.read_bytes()[:anchor['used']*2],actions=[])
    beam=[anchor];history=[];best=anchor
    L,R,J=0x200,0x100,0x8000
    patterns={'wait':[0]*40,'L':[L]*40,'R':[R]*40,'J':[J]*12+[0]*28,
        'LJ':[L]*2+[L|J]*12+[L]*26,'RJ':[R]*2+[R|J]*12+[R]*26,
        'LJR':[L]*2+[L|J]*12+[R]*26,'RJL':[R]*2+[R|J]*12+[L]*26,
        'runLJ':[L]*12+[L|J]*12+[L]*16,'runRJ':[R]*12+[R|J]*12+[R]*16,
        'JL':[J]*12+[L]*28,'JR':[J]*12+[R]*28}
    def branch(item):
        depth,index,parent,name=item;pads=patterns[name];raw=struct.pack('<40H',*pads)
        node=run(f'd{depth}-p{index}-{name}',parent['frame']+40,raw,parent['folder']/'end.state')
        assert node['used']<=40
        node.update(prefix=parent['prefix']+raw[:node['used']*2],actions=parent['actions']+[name])
        return node
    for depth in range(1,args.rounds+1):
        jobs=[(depth,index,parent,name) for index,parent in enumerate(beam) for name in patterns]
        with ThreadPoolExecutor(max_workers=3) as pool:nodes=list(pool.map(branch,jobs))
        good=[n for n in nodes if n['info']['level']==0 and n['info']['descriptor']==0x80d and
            n['info']['health']>0 and n['info']['lives']>=initial['lives'] and
            n['info']['boss_health']<=initial['boss_health']]
        if not good:break
        def score(n):
            v=n['info'];return v['boss_health']*1000+(initial['health']-v['health'])*25+abs(v['x']-v['boss_x'])*.04-(35 if v['boss_action']==0xc145d3 else 0)
        good.sort(key=score);beam=[];bins=set()
        for node in good:
            v=node['info'];key=(v['x']//24,v['y']//16,v['boss_action'],v['boss_health'])
            if key in bins:continue
            bins.add(key);beam.append(node)
            if len(beam)==3:break
        best=beam[0];history.append(dict(depth=depth,info=best['info'],actions=best['actions']))
        print('Native depth',depth,best['info'],flush=True)
        if best['info']['boss_health']==0 and best['info']['boss_action']==0xc147f7:break
    selected=out/'selected.polled.tape';selected.write_bytes(best['prefix'])
    final=run('uninterrupted',best['frame'],best['prefix'])
    assert final['ram']==best['ram'],'Uninterrupted WRAM differs from planning'
    paths=[Path(__file__),capture,tape,profile,exe,ROOT/'Lion King, The (USA).sfc']
    result=dict(result='AUTHORED' if final['info']['boss_health']==0 and final['info']['boss_action']==0xc147f7 else 'PARTIAL',
        scope=__doc__,initial=initial,final=final['info'],history=history,frames=best['frame'],
        uninterrupted_full_wram_matches_planning=True,game_or_rom_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={selected.name:digest(selected),
            f'uninterrupted/hl_wram_{best["frame"]}.bin':digest(final['folder']/f'hl_wram_{best["frame"]}.bin'),
            'uninterrupted/run.log':digest(final['folder']/'run.log')})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
