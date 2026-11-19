"""Move before roaring, using the neutral observer's genuine frame2880 save."""
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
    source=ROOT/'build/pride-walking-inputs/report.json'; prior=bound(source)
    assert all(prior['checks'].values())
    out=ROOT/'build/pride-walking-approach';out.mkdir()
    template=prior['commands']['roar-24'];commands={};cases={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for steps in (16,24,32,40,48,64):
        label=f'approach-{steps}';folder=out/label;folder.mkdir()
        pads=[0x100]*steps+[0]*4+[0x80]*30+[0]*(240-steps-34)
        tape=folder/'tail.tape';tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
        cmd=template.copy()
        for flag,value in [('--input-polled',tape),('--dump-window',folder/'window.png'),
                            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        commands[label]=cmd
        env=dict(clean,TLK_WALK_ACTOR_LOG=str(folder/'actors.csv'),TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),
                 TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        rows=list(csv.DictReader((folder/'actors.csv').open()));previous={};episodes=[]
        for r in rows:
            old=previous.get(r['actor']);previous[r['actor']]=r
            if r['actor']!='b213' and r['action']=='c15b87' and old and old['action']=='c150d7':
                episodes.append(dict(before=old,after=r))
        roar=[r for r in rows if r['actor']=='b213' and int(r['strength'])>0]
        cases[label]=dict(exit=rc,walking_entries=episodes,roar_fields=[roar[0],roar[-1]] if roar else [])
        print(label,rc,[(r['after']['field'],r['after']['timer']) for r in episodes],
              [(r['field'],r['x'],r['y'],r['strength']) for r in cases[label]['roar_fields']],flush=True)
    paths=[Path(__file__),source]
    report=dict(result='OBSERVED',commands=commands,cases=cases,ordinary_inputs_only=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
