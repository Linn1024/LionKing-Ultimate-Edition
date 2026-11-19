"""Author local controller routes using ordinary saved checkpoints.

Checkpoints are used only to explore input branches. The selected controller
prefix is always replayed from power-on and compared with the planning WRAM.
No ROM, actor, RNG, health, position or other guest fields are patched.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tape',type=Path,required=True)
    parser.add_argument('--frame',type=int,required=True)
    parser.add_argument('--profile',type=Path,default=ROOT/'build/pride-route-candidate/resources.ini')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--step',type=int,default=40)
    parser.add_argument('--rounds',type=int,default=12)
    parser.add_argument('--beam',type=int,default=6)
    parser.add_argument('--target-x',type=int,default=1050)
    parser.add_argument('--goal-y',type=int)
    parser.add_argument('--goal-x',type=int)
    parser.add_argument('--goal-x-max',type=int)
    parser.add_argument('--prefer-right',action='store_true')
    parser.add_argument('--combat',action='store_true')
    parser.add_argument('--boss-actor',type=lambda v:int(v,0),default=0xba13)
    args=parser.parse_args();assert 16<=args.step<=120 and args.rounds>0 and args.beam>0
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    assert args.tape.resolve()!=(out/'best.polled.tape').resolve(),'Use a new output directory when resuming a route'
    source_hash=digest(args.tape)
    host=ROOT/'engine/build-win/tlk_headless.exe';host_hash=digest(host);profile_hash=digest(args.profile)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    base=[host,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
          '--resource-profile',args.profile]
    def run(name,frame,tape,state=None):
        folder=out/name;folder.mkdir(exist_ok=True)
        env=os.environ.copy();env.update(TLK_WRAM_DUMP=str(frame),TLK_WRAM_DIR=str(folder))
        cmd=base+['--frames',frame,'--input-polled',tape,'--ram-log',folder/'game.ram',
                  '--save-at',frame,folder/'end.state']
        if state:cmd+=['--load',state]
        with (folder/'game.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        used=int(re.search(r'tape_words_used=(\d+)',(folder/'game.log').read_text()).group(1))
        ram=(folder/f'hl_wram_{frame}.bin').read_bytes()
        word=lambda at:struct.unpack_from('<H',ram,at)[0]
        info={'x':word(0xb21b),'y':word(0xb21d),'health':word(0x2004),'lives':word(0x1ffaa),
              'level':word(0x1ff9e),'state':word(0xb243)|word(0xb245)<<16}
        if args.combat:
            actor=args.boss_actor
            info.update(boss_health=word(actor+42),boss_cycle=word(actor+40),boss_x=word(actor+8),
                        boss_state=word(actor+48)|word(actor+50)<<16)
        return folder,used,info
    folder,used,initial=run('anchor',args.frame,args.tape)
    raw=args.tape.read_bytes();prefix=list(struct.unpack('<'+'H'*(len(raw)//2),raw))[:used]
    beam=[{'folder':folder,'frame':args.frame,'prefix':prefix,'info':initial,'actions':[]}]
    step=args.step;hold=min(12,step//3);lead=min(12,step//3);L=0x200;R=0x100;B=0x8000;U=0x800
    patterns={'wait':[0]*step,'L':[L]*step,'R':[R]*step,'roar':[0]*2+[0x80]*6+[0]*(step-8)}
    for name,direction,opposite in [('L',L,R),('R',R,L)]:
        patterns[name+'J']=[direction]*2+[direction|B]*hold+[direction]*(step-2-hold)
        patterns['run'+name+'J']=[direction]*lead+[direction|B]*hold+[direction]*(step-lead-hold)
        patterns[name+'J'+('R' if name=='L' else 'L')]=[direction]*2+[direction|B]*hold+[direction]*2+[opposite]*(step-4-hold)
        patterns['U'+name+'J']=[direction|U]*2+[direction|U|B]*hold+[direction|U]*(step-2-hold)
        patterns['J'+name]=[0]*2+[B]*hold+[direction]*(step-2-hold)
    patterns['J']=[0]*2+[B]*hold+[0]*(step-2-hold)
    def branch(item):
        depth,index,parent,action=item;values=patterns[action]
        name=f'd{depth}-p{index}-{action}';tape=out/(name+'.polled.tape')
        tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
        frame=parent['frame']+step;folder,used,info=run(name,frame,tape,parent['folder']/'end.state')
        assert used<=len(values)
        return {'folder':folder,'frame':frame,'prefix':parent['prefix']+values[:used],
                'info':info,'actions':parent['actions']+[{'name':action,'consumed_polls':used}]}
    def score(node):
        v=node['info']
        if args.combat:
            return min(v['boss_health'],3)*1000+v['boss_cycle']*10+(6-v['health'])*8+abs(v['x']-v['boss_x'])*.03-(35 if v['boss_state']==0xc145d3 else 0)
        if args.prefer_right:return -v['x']*.4+v['y']*.2+(6-v['health'])*10
        return v['y']+abs(v['x']-args.target_x)*.03+(6-v['health'])*3
    history=[];best=beam[0];waypoint=False
    for depth in range(1,args.rounds+1):
        jobs=[(depth,i,parent,action) for i,parent in enumerate(beam) for action in patterns]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:nodes=list(pool.map(branch,jobs))
        completed=[n for n in nodes if n['info']['level']==initial['level']+1]
        good=[n for n in nodes if n['info']['level']==initial['level'] and n['info']['lives']>=initial['lives'] and n['info']['health']>0 and n['info']['y']<max(800,initial['y']+150)]
        good.sort(key=score);beam=[];bins=set()
        for node in completed or good:
            v=node['info'];key=(v['x']//24,v['y']//16,v['state'])
            if key in bins:continue
            bins.add(key);beam.append(node)
            if len(beam)==args.beam:break
        if not beam:break
        best=beam[0]
        summary=[{k:str(v) if k=='folder' else v for k,v in n.items() if k!='prefix'} for n in beam]
        history.append(summary)
        (out/'search.json').write_text(json.dumps({'result':'RUNNING','planning_loads_only':True,'generations':history},indent=2)+'\n')
        (out/'best.polled.tape').write_bytes(struct.pack('<'+'H'*len(best['prefix']),*best['prefix']))
        print('depth',depth,best['info'],flush=True)
        waypoint=any(value is not None for value in (args.goal_x,args.goal_x_max,args.goal_y)) and (args.goal_x is None or best['info']['x']>=args.goal_x) and (args.goal_x_max is None or best['info']['x']<=args.goal_x_max) and (args.goal_y is None or best['info']['y']<=args.goal_y)
        if completed or waypoint:break
    tape=out/'best.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(best['prefix']),*best['prefix']))
    replay,_,observed=run('uninterrupted',best['frame'],tape)
    name=f"hl_wram_{best['frame']}.bin"
    assert (replay/name).read_bytes()==(best['folder']/name).read_bytes(),'Planning versus uninterrupted full WRAM differs'
    assert digest(host)==host_hash and digest(args.profile)==profile_hash,'Host/profile changed during planning'
    report={'result':'PARTIAL','scope':__doc__,'headless_sha256':host_hash,'profile_sha256':profile_hash,
            'source_tape_sha256':source_hash,'selected_tape_sha256':digest(tape),'anchor_frame':args.frame,
            'final_frame':best['frame'],'initial':initial,'final':observed,'waypoint_reached':waypoint,
            'waypoint_bounds':{'x_min':args.goal_x,'x_max':args.goal_x_max,'y_max':args.goal_y},
            'next_level_reached':observed['level']==initial['level']+1,'uninterrupted_full_wram_matches_planning':True,
            'full_first_level_fidelity_proven':False,'planning_actions':best['actions']}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    (out/'search.json').write_text(json.dumps({'result':'PARTIAL','planning_loads_only':True,'generations':history},indent=2)+'\n')
    print('Uninterrupted controller replay matches planning:',observed,flush=True)


if __name__=='__main__':main()
