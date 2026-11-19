"""Qualify a read-only actor logger and search ordinary input branches from a save."""
import csv
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
    out = ROOT/'build/pride-walking-inputs'; out.mkdir()
    source = ROOT/'build/pride-walking-guest-context2/report.json'
    control = bound(source)['commands']['normal'].copy()
    observer = ROOT/'build/pride-sprite-fresh44/walking-observer'
    observer_build = observer/'build-report.json'; build = bound(observer_build)
    assert build['nonhost_inputs_unchanged'] == 321
    assert all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    commands = {}; checks = {}
    def run(label, frames, tape=None, load=None, observe=True, save=False):
        folder = out/label; folder.mkdir(); cmd = control.copy()
        if observe: cmd[0] = str(observer/'player.exe')
        for flag, value in [('--frames',frames),('--dump-window',folder/'window.png'),
                            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:
            cmd[cmd.index(flag)+1] = str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if tape: cmd[cmd.index('--input-polled')+1] = str(tape)
        if load: cmd += ['--load',str(load)]
        if save: cmd += ['--save-at',str(frames),str(folder/'saved.state')]
        if not load: cmd += ['--hash-at',','.join(map(str,range(1,frames+1)))]
        commands[label] = cmd
        env=dict(clean,TLK_WALK_ACTOR_LOG=str(folder/'actors.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),
                 TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exit']=rc==0
        print(label,rc,flush=True)
        return folder
    a=run('seed-control',2880,observe=False,save=True)
    b=run('seed-observer',2880,save=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    checks['all2880_guest_fields_neutral']=len(rows(a))==2880 and rows(a)==rows(b)
    for name in ('window.png','scene.json','audio.wav','tree.jsonl','events.csv','attack.csv'):
        checks[name+'_neutral']=digest(a/name)==digest(b/name)
    if not all(checks.values()): raise AssertionError(checks)
    row=json.loads((b/'tree.jsonl').read_text().splitlines()[-1]); assert row['field']==2880
    cases={}
    for delay in (24,40,48,56,64,72,80,96,112):
        pads=[0]*delay+[0x80]*24+[0]*max(0,240-delay-24)
        tape=out/f'roar-{delay}.tail.tape';tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
        folder=run(f'roar-{delay}',3120,tape=tape,load=b/'saved.state')
        actor_rows=list(csv.DictReader((folder/'actors.csv').open()))
        episodes=[];previous={}
        for current in actor_rows:
            actor=current['actor'];last=previous.get(actor);previous[actor]=current
            if actor!='b213' and current['action']=='c15b87' and last and last['action']=='c150d7':
                episodes.append(dict(before=last,after=current))
        roaring=[r for r in actor_rows if r['actor']=='b213' and int(r['strength'])>0]
        cases[str(delay)]=dict(walking_entries=episodes,roar_fields=[roaring[0],roaring[-1]] if roaring else [],
                              player_actions=sorted({r['action'] for r in actor_rows if r['actor']=='b213'}))
        print(delay,[(e['after']['field'],e['after']['timer']) for e in episodes],cases[str(delay)]['player_actions'],flush=True)
    paths=[Path(__file__),source,observer_build]
    report=dict(result='OBSERVED',checks=checks,commands=commands,cases=cases,seed_poll_index=row['poll_index'],
                ordinary_inputs_only=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()
