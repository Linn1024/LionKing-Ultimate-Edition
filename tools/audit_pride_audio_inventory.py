"""Inventory actual Pride sound events and unclassified first-level callers."""
import collections
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-audio-inventory-current';out.mkdir()
    binary=ROOT/'build/pride-arena-work/tlk_pride_player.exe'
    profile=ROOT/'build/pride-title-work/completion/resources.ini'
    tape=ROOT/'build/pride-rng-player4/width-fight1/best.polled.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
         '--config',config,'--resource-profile',profile,'--input-polled',tape,'--frames',4500,
         '--no-pace','--no-audio','--no-record','--dump-window',out/'window.png','--dump-scene',out/'scene.json']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env['TLK_AUDIO_EVENTS']=str(out/'events.csv')
    with (out/'run.log').open('wb') as log:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    source=ROOT/'engine/runner/tlk_audio.c';text=source.read_text()
    table=text.split('cues[]={',1)[1].split('\n};',1)[0]
    cues=[]
    for resource,event,selector,value,actor,caller in re.findall(r'\{"([^"]+)",([^,]+),([^,]+),([^,]+),([^,]+),([^}]+)\}',table):
        cues.append(dict(resource=resource,event=int(event,0),actor=int(actor,0),caller=int(caller,0)))
    inventory=collections.Counter();unclassified=collections.Counter()
    for row in csv.DictReader((out/'events.csv').open()):
        if row['level']!='0000' or row['descriptor'] not in ('0387','080d'):continue
        event=int(row['event'],16);actor=int(row['actor'],16);stack=bytes.fromhex(row['stack'])
        caller=(stack[7]<<16)|((int.from_bytes(stack[5:7],'little')+1)&65535)
        matches=[c['resource'] for c in cues if c['event']==event and (c['actor']==1)==(actor==0xb213) and (not c['caller'] or c['caller']==caller)]
        key=(f'{event:04x}',f'{caller:06x}',actor==0xb213,tuple(matches))
        inventory[key]+=1
        if event>2 and not matches:unclassified[key]+=1
    rows=lambda counter:[dict(event=k[0],caller=k[1],simba=k[2],resources=k[3],count=v) for k,v in sorted(counter.items())]
    paths=[Path(__file__),binary,profile,tape,source]
    scene=json.loads((out/'scene.json').read_text());assert scene['level']==1
    report=dict(result='INVENTORIED',reached_next_level=True,inventory=rows(inventory),unclassified=rows(unclassified),
                complete_audio_coverage_proven=False,command=list(map(str,cmd)),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(events=len(inventory),unclassified=report['unclassified'])),flush=True)


if __name__=='__main__':main()
