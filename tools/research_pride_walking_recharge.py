"""Recharge naturally on the reached ledge, climb and roar at the walking NPC."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    source=ROOT/'build/pride-walking-approach/report.json';prior=bound(source)
    out=ROOT/'build/pride-walking-recharge';out.mkdir()
    template=prior['commands']['approach-48'];commands={};checks={};cases={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(label,frames,tape=None,load=None,save=False):
        folder=out/label;folder.mkdir();cmd=template.copy()
        for flag,value in [('--frames',frames),('--dump-window',folder/'window.png'),
                            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if tape:cmd[cmd.index('--input-polled')+1]=str(tape)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(frames),str(folder/'saved.state')]
        commands[label]=cmd
        env=dict(clean,TLK_WALK_ACTOR_LOG=str(folder/'actors.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),
                 TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exit']=rc==0;print(label,rc,flush=True);return folder
    seed=run('ledge-seed',3120,save=True)
    for name in ('window.png','scene.json','audio.wav','actors.csv'):
        checks['seed_'+name+'_exact']=digest(seed/name)==digest(source.parent/'approach-48'/name)
    if not all(checks.values()):raise AssertionError(checks)
    for label,button,held in [('up16',0x800,16),('up32',0x800,32),('up64',0x800,64),('jump16',0x8000,16)]:
        pads=[0]*768+[button]*held+[0]*24+[0x80]*24+[0]*120
        tape=out/(label+'.tail.tape');tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
        folder=run(label,3120+len(pads),tape=tape,load=seed/'saved.state')
        rows=list(csv.DictReader((folder/'actors.csv').open()));previous={};episodes=[]
        for r in rows:
            old=previous.get(r['actor']);previous[r['actor']]=r
            if r['actor']!='b213' and r['action']=='c15b87' and old and old['action']=='c150d7':episodes.append(dict(before=old,after=r))
        roar=[r for r in rows if r['actor']=='b213' and int(r['strength'])>0]
        player=[r for r in rows if r['actor']=='b213']
        cases[label]=dict(walking_entries=episodes,roar_fields=[roar[0],roar[-1]] if roar else [],last_player=player[-1])
        print(label,[(r['after']['field'],r['after']['timer']) for r in episodes],
              [(r['field'],r['x'],r['y'],r['strength']) for r in cases[label]['roar_fields']],flush=True)
    paths=[Path(__file__),source]
    report=dict(result='OBSERVED',checks=checks,commands=commands,cases=cases,ordinary_inputs_only=True,
                guest_or_rom_edits=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
