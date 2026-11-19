"""Explore the floor-query gap from the verified lower route using controls only."""
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
    out=ROOT/'build/pride-lower-fall136';out.mkdir()
    reference=ROOT/'build/pride-fall-lower-route/report.json';prior=bound(reference);assert prior['result']=='PASS'
    geometry=ROOT/'build/pride-bottom-floor135/report.json';assert all(bound(geometry)['checks'].values())
    host=ROOT/'engine/build-win/tlk_headless.exe'
    assert digest(host)==prior['source_sha256']['engine/build-win/tlk_headless.exe']
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    original=reference.parent/'poweron.polled.tape';seed=out/'anchor.state'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_RAM_LOG_DEATH']='1'
    commands={}
    def run(label,frames,tape,load=None,save=None):
        folder=out/label;folder.mkdir()
        cmd=[str(host),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--resource-profile',str(profile),'--input-polled',str(tape),'--frames',str(frames),'--lle','--ram-log',str(folder/'game.ram')]
        if load:cmd+=['--load',str(load)]
        if save:cmd+=['--save-at',str(frames),str(save)]
        with (folder/'run.log').open('wb') as log:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        assert p.returncode==0,(label,p.returncode)
        commands[label]=cmd
        return [line.split() for line in (folder/'game.ram').read_text().splitlines()]
    anchor=run('anchor',3200,original,save=seed)
    assert (out/'anchor/game.ram').read_bytes()==(reference.parent/'reference/game.ram').read_bytes()
    log=(out/'anchor/run.log').read_text();used=int(re.search(r'tape_words_used=(\d+)',log)[1]);prefix=original.read_bytes()[:used*2]
    patterns=dict(right300=[0x100]*300+[0]*200,right500=[0x100]*500,
        roll300=[0x100]*12+[0x500]*288+[0]*200,
        right90_jump=[0x100]*90+[0x8100]*24+[0x100]*186+[0]*200,
        right100_jump=[0x100]*100+[0x8100]*24+[0x100]*176+[0]*200,
        right110_jump=[0x100]*110+[0x8100]*24+[0x100]*166+[0]*200)
    cases={}
    for label,pads in patterns.items():
        tape=out/(label+'.polled.tape');tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
        rows=run(label,3700,tape,load=seed);deaths=[]
        for i,row in enumerate(rows):
            if i and int(row[3],16)==0 and int(rows[i-1][3],16)>0:
                deaths.append(dict(field=int(row[0]),x=int(row[4],16),y=int(row[5],16),before_y=int(rows[i-1][5],16),skip=int(row[9],16)))
        fall=next((d for d in deaths if d['before_y']>1575),None)
        cases[label]=dict(deaths=deaths,fall=fall,max_y=max(int(r[5],16) for r in rows),max_x=max(int(r[4],16) for r in rows),final_xy=[int(rows[-1][4],16),int(rows[-1][5],16)])
        if fall:
            full=out/(label+'-poweron.polled.tape');full.write_bytes(prefix+tape.read_bytes())
            replay=run(label+'-poweron',3700,full)
            cases[label]['uninterrupted_rows_exact']=replay[-len(rows):]==rows
            cases[label]['poweron_tape']=full.relative_to(ROOT).as_posix()
        print(label,cases[label],flush=True)
        (out/'partial.json').write_text(json.dumps(cases,indent=2)+'\n')
    paths=[Path(__file__),reference,geometry,host,original,profile,ROOT/'Lion King, The (USA).sfc']
    report=dict(result='FOUND' if any(c['fall'] for c in cases.values()) else 'NOT_FOUND',cases=cases,commands=commands,anchor_polled_words=used,
        checks=dict(verified_lower_route_reproduced=True,all_six_branches_completed=len(cases)==6),
        no_actor_rom_or_rng_edits=True,planning_checkpoints_only=True,
        scope='Original native lower-route continuation through ordinary inputs towards bottom floor-query gaps; bounded search, not a proof that fall death is unreachable or an MD/runtime adapter qualification.',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)
if __name__=='__main__':main()
