"""Author ordinary controls using current player saves and verify a cold WRAM replay."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tape',type=Path,required=True);p.add_argument('--profile',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--frame',type=int,required=True)
    p.add_argument('--player',type=Path,default=ROOT/'build/pride-rng-player4/width-observer/player.exe')
    p.add_argument('--step',type=int,default=40);p.add_argument('--rounds',type=int,default=12)
    p.add_argument('--beam',type=int,default=3);p.add_argument('--boss',type=lambda n:int(n,0))
    p.add_argument('--target-x',type=int,default=600);p.add_argument('--goal-x',type=int)
    p.add_argument('--goal-x-max',type=int);p.add_argument('--goal-y',type=int)
    args=p.parse_args();assert args.frame>0 and 32<=args.step<=120 and args.rounds>0 and args.beam>0
    out=args.out.resolve();assert ROOT/'build' in out.parents;out.mkdir()
    player=args.player.resolve();profile=args.profile.resolve();original=args.tape.resolve()
    bp=player.parent/'build-report.json';build=bound(bp);assert digest(player)==build['binary_sha256']
    profile_hash=digest(profile);original_hash=digest(original)
    read_words=lambda path:list(struct.unpack('<'+'H'*(path.stat().st_size//2),path.read_bytes()))
    values=read_words(original)
    # Implicit neutral input after EOF is not counted by the frontend. Expand
    # it before anchoring so concatenated branch controls keep their timing.
    values += [0]*((args.frame+args.rounds*args.step+2000)*2)
    padded=out/'anchor-input.polled.tape';padded.write_bytes(struct.pack('<'+'H'*len(values),*values))
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};refused=[]
    def run(name,frame,tape,state=None):
        folder=out/name;folder.mkdir()
        env=dict(clean,SDL_VIDEODRIVER='dummy',TLK_OBS_DUMP_FIELDS=str(frame),TLK_OBS_DUMP_DIR=str(folder))
        cmd=[player,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',frame,
             '--no-pace','--no-audio','--no-record','--wav',folder/'audio.wav','--wav-seconds',240,
             '--save-at',frame,folder/'end.state']
        if state:cmd+=['--load',state]
        commands[name]=list(map(str,cmd))
        with (folder/'game.log').open('wb') as log:
            result=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=150)
        save_refused=result.returncode==8 and 'cannot save state ' in (folder/'game.log').read_text()
        assert result.returncode==0 or save_refused,(name,result.returncode)
        if save_refused:refused.append(name)
        ram_path=folder/f'wram-{frame}.bin';ram=ram_path.read_bytes();assert len(ram)==0x20000
        w=lambda at:struct.unpack_from('<H',ram,at)[0]
        info=dict(x=w(0xb21b),y=w(0xb21d),health=w(0x2004),lives=w(0x1ffaa),level=w(0x1ff9e),
                  state=w(0xb243)|w(0xb245)<<16,exit_flag=w(0x1ff90),state_saved=not save_refused)
        if args.boss:
            a=args.boss;info.update(boss_health=w(a+42),boss_cycle=w(a+40),boss_x=w(a+8),boss_state=w(a+48)|w(a+50)<<16)
        used=int(next(csv.DictReader((folder/f'input-{frame}.csv').open()))['polls_used'])
        return folder,used,info
    anchor,used,initial=run('anchor',args.frame,padded)
    assert initial['state_saved'] and used<len(values),'Anchor unavailable or explicit neutral tail exhausted'
    beam=[dict(folder=anchor,frame=args.frame,prefix=values[:used],info=initial,actions=[])]
    step=args.step;hold=min(24,step-14);lead=min(12,step//3);L=0x200;R=0x100;B=0x8000;U=0x800
    patterns={'wait':[0]*step,'L':[L]*step,'R':[R]*step,'roar':[0]*2+[0x80]*6+[0]*(step-8)}
    for name,direction,opposite in (('L',L,R),('R',R,L)):
        patterns[name+'J']=[direction]*2+[direction|B]*hold+[direction]*(step-2-hold)
        patterns['run'+name+'J']=[direction]*lead+[direction|B]*hold+[direction]*(step-lead-hold)
        patterns[name+'J'+('R' if name=='L' else 'L')]=[direction]*2+[direction|B]*hold+[direction]*2+[opposite]*(step-4-hold)
        patterns['U'+name+'J']=[direction|U]*2+[direction|U|B]*hold+[direction|U]*(step-2-hold)
        patterns['J'+name]=[0]*2+[B]*hold+[direction]*(step-2-hold)
    patterns['J']=[0]*2+[B]*hold+[0]*(step-2-hold)
    def branch(job):
        depth,index,parent,action=job;words=patterns[action];name=f'd{depth}-p{index}-{action}'
        tape=out/(name+'.polled.tape');tape.write_bytes(struct.pack('<'+'H'*len(words),*words))
        frame=parent['frame']+step;folder,used,info=run(name,frame,tape,parent['folder']/'end.state');assert used<=len(words)
        return dict(folder=folder,frame=frame,prefix=parent['prefix']+words[:used],info=info,
                    actions=parent['actions']+[dict(name=action,consumed_polls=used)])
    def terminal(node):
        v=node['info']
        if v['level']==initial['level']+1:return True
        if args.boss and v['boss_health']==0 and v['exit_flag']:return True
        return any(x is not None for x in (args.goal_x,args.goal_x_max,args.goal_y)) and all((
            args.goal_x is None or v['x']>=args.goal_x,args.goal_x_max is None or v['x']<=args.goal_x_max,
            args.goal_y is None or v['y']<=args.goal_y))
    def score(node):
        v=node['info']
        if args.boss:return min(v['boss_health'],3)*1000+v['boss_cycle']*10+(6-v['health'])*8+abs(v['x']-v['boss_x'])*.03-(35 if v['boss_state']==0xc145d3 else 0)
        return v['y']+abs(v['x']-args.target_x)*.15+(6-v['health'])*3
    history=[];best=beam[0];reached=False
    for depth in range(1,args.rounds+1):
        jobs=[(depth,i,node,action) for i,node in enumerate(beam) for action in patterns]
        with ThreadPoolExecutor(max_workers=4) as pool:nodes=list(pool.map(branch,jobs))
        live=[n for n in nodes if n['info']['lives']>=initial['lives'] and n['info']['health']>0]
        ends=sorted((n for n in live if terminal(n)),key=score)
        good=ends or sorted((n for n in live if n['info']['level']==initial['level'] and n['info']['state_saved'] and
                            n['info']['y']<max(800,initial['y']+150)),key=score)
        beam=[];bins=set()
        for node in good:
            v=node['info'];key=(v['x']//24,v['y']//16,v['state'])
            if key in bins:continue
            bins.add(key);beam.append(node)
            if len(beam)==args.beam:break
        if not beam:break
        best=beam[0];reached=terminal(best)
        history.append([{k:str(v) if k=='folder' else v for k,v in n.items() if k!='prefix'} for n in beam])
        (out/'search.json').write_text(json.dumps(dict(result='RUNNING',generations=history),indent=2)+'\n')
        print('depth',depth,best['info'],flush=True)
        if reached:break
    tape=out/'best.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(best['prefix']),*best['prefix']))
    cold,_,observed=run('uninterrupted',best['frame'],tape)
    name=f"wram-{best['frame']}.bin";assert (cold/name).read_bytes()==(best['folder']/name).read_bytes()
    assert digest(player)==build['binary_sha256'] and digest(profile)==profile_hash and digest(original)==original_hash
    paths=[Path(__file__),bp,original,profile,padded,tape,cold/name,best['folder']/name]
    result=dict(result='PARTIAL',goal_reached=reached,initial=initial,final=observed,final_frame=best['frame'],
        selected_tape_sha256=digest(tape),planning_actions=best['actions'],refused_save_branches=sorted(refused),
        uninterrupted_full_wram_matches_planning=True,normal_poweron_final_replay=True,loaded_states_in_final_replay=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},commands=commands,
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Cold full-WRAM replay exact',observed,flush=True)


if __name__=='__main__':main()
