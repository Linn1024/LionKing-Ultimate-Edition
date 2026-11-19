"""Find a genuine Pride fall using ordinary controls from a reached checkpoint."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-fall-native-routes';out.mkdir()
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    host=ROOT/'engine/build-win/tlk_headless.exe';tape=ROOT/'engine/tapes/allbugsF.read.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env['TLK_RAM_LOG_DEATH']='1'
    commands={};cases={}
    def run(label,frame,recording,load=None,save=None):
        folder=out/label;folder.mkdir()
        cmd=list(map(str,[host,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,
                          '--input-polled',recording,'--frames',frame,'--lle','--ram-log',folder/'game.ram']))
        if load:cmd+=['--load',str(load)]
        if save:cmd+=['--save-at',str(frame),str(save)]
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.returncode==0
        commands[label]=cmd
        return [line.split() for line in (folder/'game.ram').read_text().splitlines()]
    seed=out/'anchor.state';run('anchor',2200,tape,save=seed)
    log=(out/'anchor/run.log').read_text();used=int(re.search(r'tape_words_used=(\d+)',log)[1])
    prefix=tape.read_bytes()[:used*2]
    patterns={'neutral':[0]*400}
    for direction,pad in [('left',0x200),('right',0x100)]:
        for duration in (20,40,80):patterns[direction+str(duration)]=[pad]*duration+[0]*(400-duration)
    for label,pads in patterns.items():
        tail=out/(label+'.polled.tape');tail.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
        rows=run(label,2600,tail,load=seed)
        deaths=[]
        for i,row in enumerate(rows):
            if i and int(row[3],16)==0 and int(rows[i-1][3],16)>0:
                deaths.append(dict(frame=int(row[0]),x=int(row[4],16),y=int(row[5],16),before_y=int(rows[i-1][5],16),skip=int(row[9],16)))
        fall=next((r for r in deaths if r['before_y']>1575),None)
        cases[label]=dict(deaths=deaths,fall=fall,final_xy=[int(rows[-1][4],16),int(rows[-1][5],16)])
        if fall:
            full=out/(label+'-poweron.polled.tape');full.write_bytes(prefix+tail.read_bytes())
            uninterrupted=run(label+'-poweron',2600,full)
            cases[label]['uninterrupted_rows_exact']=uninterrupted[-len(rows):]==rows
            cases[label]['poweron_tape']=full.relative_to(ROOT).as_posix()
        print(label,cases[label],flush=True)
    paths=[Path(__file__),host,tape,profile]
    report=dict(result='FOUND' if any(c['fall'] for c in cases.values()) else 'NOT_FOUND',cases=cases,commands=commands,anchor_polled_words=used,
                no_actor_rom_or_rng_edits=True,planning_checkpoints_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)


if __name__=='__main__':main()
