"""Author ordinary Difficult controls with selected MD art/audio on public53.

Only current-build checkpoints and controller branches are used. Stop at owned
boss death; replay the complete selected tape from power-on before qualifying it.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    source=ROOT/'build/pride-hyena-mixtures58/report.json';prior=bound(source)
    assert [k for k,v in prior['checks'].items() if not v]==['hard-mixed-aot_owned_boss_death','hard-mixed-lle_owned_boss_death']
    out=ROOT/'build/pride-hyena-mixed-plan58';out.mkdir();template=prior['commands']['hard-mixed-aot'].copy()
    for flag,count in [('--save-at',3),('--hash-at',2),('--dump-window',2),('--dump-scene',2)]:
        i=template.index(flag);del template[i:i+count]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    initial_folder=source.parent/'hard-mixed-aot';state=initial_folder/'current.state'
    tree=[json.loads(r) for r in (initial_folder/'tree.jsonl').read_text().splitlines()]
    row=next(r for r in tree if r['field']==4555)
    original_tape=Path(template[template.index('--input-polled')+1]);prefix=original_tape.read_bytes()[:row['poll_index']*2]
    initial_raw=(source.parent/'hard-tail-analysis/verified-wram.bin').read_bytes()
    def info(ram):
        word=lambda at:struct.unpack_from('<H',ram,at)[0]
        ptr=lambda at:word(at)|ram[at+2]<<16
        actor=0xba13;draw=word(actor+12)
        return dict(level=word(0x1ff9e),scene=ptr(0xdf),health=word(0x2004),lives=word(0x1ffaa),
            x=word(0xb21b),y=word(0xb21d),boss_x=word(actor+8),boss_y=word(actor+10),boss_health=word(actor+0x2a),
            boss_action=ptr(actor+0x30),boss_timer=word(actor+0x2c),boss_owned=ptr(actor+4)==0xc58c68 and
            0x8000<=draw<=0xffe8 and word(draw+4)==actor+8)
    initial=info(initial_raw);assert initial['boss_owned'] and initial['boss_health']==2 and initial['health']>0
    commands={}
    def run(label,end,raw,load=None,mode='aot'):
        folder=out/label;folder.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]=str(end)
        tape=folder/'inputs.polled.tape';tape.write_bytes(raw);cmd[cmd.index('--input-polled')+1]=str(tape)
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/file;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        cmd[cmd.index('--wav')+1]=str(folder/'audio.wav')
        cmd+=['--save-at',str(end),str(folder/'current.state')]
        if load:cmd+=['--load',str(load)]
        if mode=='lle':cmd+=['--lle']
        commands[label]=cmd
        with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
        text=(folder/'run.log').read_text();expected=re.findall(r'^wram_sha256=([a-f0-9]+)',text,re.M)[-1]
        data=(folder/'current.state').read_bytes();assert data[:8]==b'TLKSTAT1' and struct.unpack_from('<I',data,8)[0]==4
        length=struct.unpack_from('<Q',data,24)[0];blob=data[36:36+length]
        # Exact53 offset discovered from a full-hash-verified current snapshot.
        # Every extraction must still match the independent logged full hash.
        ram=blob[166265:166265+0x20000];assert hashlib.sha256(ram).hexdigest()==expected
        used=int(re.search(r'tape_words_used=(\d+)',text).group(1))
        return dict(folder=folder,frame=end,ram=ram,info=info(ram),used=used)
    initial_node=dict(folder=initial_folder,frame=4555,ram=initial_raw,info=initial,prefix=prefix,actions=[])
    beam=[initial_node];history=[];best=initial_node
    L,R,J=0x200,0x100,0x8000
    patterns={'wait':[0]*40,'L':[L]*40,'R':[R]*40,'J':[J]*12+[0]*28,
        'LJ':[L]*2+[L|J]*12+[L]*26,'RJ':[R]*2+[R|J]*12+[R]*26,
        'LJR':[L]*2+[L|J]*12+[R]*26,'RJL':[R]*2+[R|J]*12+[L]*26,
        'runLJ':[L]*12+[L|J]*12+[L]*16,'runRJ':[R]*12+[R|J]*12+[R]*16,
        'JL':[J]*12+[L]*28,'JR':[J]*12+[R]*28}
    def branch(job):
        depth,index,parent,name=job;raw=struct.pack('<40H',*patterns[name])
        node=run(f'd{depth:02d}-p{index}-{name}',parent['frame']+40,raw,parent['folder']/'current.state')
        assert node['used']<=40
        node.update(prefix=parent['prefix']+raw[:node['used']*2],actions=parent['actions']+[name]);return node
    for depth in range(1,21):
        jobs=[(depth,index,parent,name) for index,parent in enumerate(beam) for name in patterns]
        with ThreadPoolExecutor(max_workers=3) as pool:nodes=list(pool.map(branch,jobs))
        good=[n for n in nodes if n['info']['level']==0 and n['info']['scene']==0xc0080d and n['info']['boss_owned'] and
              n['info']['health']>0 and n['info']['lives']==initial['lives'] and n['info']['boss_health']<=initial['boss_health']]
        if not good:break
        def score(n):
            v=n['info'];return v['boss_health']*1000+(initial['health']-v['health'])*35+abs(v['x']-v['boss_x'])*.12-(35 if v['boss_action']==0xc145d3 else 0)
        good.sort(key=score);beam=[];bins=set()
        for node in good:
            v=node['info'];key=(v['x']//24,v['y']//16,v['boss_action'],v['boss_health'])
            if key in bins:continue
            bins.add(key);beam.append(node)
            if len(beam)==2:break
        best=beam[0];history.append(dict(depth=depth,info=best['info'],actions=best['actions']))
        print('depth',depth,best['info'],best['actions'],flush=True)
        if best['info']['boss_health']==0 and best['info']['boss_action']==0xc147f7:break
    tape=out/'selected.polled.tape';tape.write_bytes(best['prefix'])
    a=run('fresh-aot',best['frame'],best['prefix']);b=run('fresh-lle',best['frame'],best['prefix'],mode='lle')
    checks=dict(ordinary_controller_victory=best['info']['boss_health']==0 and best['info']['boss_action']==0xc147f7,
                uninterrupted_aot_full_wram_equals_planning=a['ram']==best['ram'],uninterrupted_lle_full_wram_equals_planning=b['ram']==best['ram'],
                no_life_lost=a['info']['lives']==initial['lives'] and a['info']['health']>0,
                entire_replay_pcm_mode_parity=digest(a['folder']/'audio.wav')==digest(b['folder']/'audio.wav'))
    paths=[Path(__file__),source,original_tape,state,source.parent/'hard-tail-analysis/verified-wram.bin']
    report=dict(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,commands=commands,history=history,
                frames=best['frame'],final=a['info'],initial=initial,controller_protocols=best['actions'],
                guest_or_rom_edits=False,planning_loads_used=True,qualification_replays_load_no_states=True,
                original_md_input_history_equivalence_claimed=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
