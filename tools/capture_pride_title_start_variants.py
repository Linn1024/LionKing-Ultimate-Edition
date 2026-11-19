"""Observe real first movement and second-Start effects with a neutral observer."""
import csv
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def spans(rows):
    rows=[r for r in rows if int(r['age'])>=515]
    return [(key,int(group[0]['age']),int(group[-1]['age'])) for key,g in itertools.groupby(rows,lambda r:int(r['lit'])>0) if (group:=list(g))]


def main():
    base=ROOT/'build/pride-title-start-native';old=bound(base/'report.json')
    original=ROOT/'build/pride-title-start-original2/report.json';md=bound(original)
    out=base/'variants';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    neutral=list(csv.DictReader((base/'320/frames.csv').open()))
    for label in ('right','second-start'):
        for mode in ('normal','lle'):
            folder=out/f'{label}-{mode}';folder.mkdir();cmd=old['commands']['320'].copy()
            data=bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
            if label=='right':
                for age in range(516,1116):struct.pack_into('<H',data,(4444+age-1)*2,0x100)
            else:struct.pack_into('<H',data,(4444+600-1)*2,0x1000)
            tape=folder/'input.tape';tape.write_bytes(data)
            for flag,value in [('--input',tape),('--config',out/'host.ini'),('--dump-window',folder/'window.png'),
                               ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
            if mode=='lle':cmd.append('--lle')
            with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1',TLK_TITLE_START_DIR=str(folder)),
                stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
            checks[folder.name+'_exit']=r.returncode==0;commands[folder.name]=cmd
            rows=list(csv.DictReader((folder/'frames.csv').open()))
            observations[folder.name]=dict(lit_spans=spans(rows),first_main_displacement=next((int(a['age']) for a,b in zip(rows,neutral)
                if a['descriptor']==b['descriptor']=='c00387' and (a['x'],a['y'])!=(b['x'],b['y'])),None))
            print(folder.name,r.returncode,observations[folder.name],flush=True)
        a=out/(label+'-normal');b=out/(label+'-lle')
        checks[label+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
        checks[label+'_trace']=(a/'frames.csv').read_bytes()==(b/'frames.csv').read_bytes()
    observations['native_neutral_lit_spans']=spans(neutral)
    observations['md_lit_spans']={label:spans(row['frames']) for label,row in md['observations'].items()}
    observations['md_first_displacement']=next((a['age'] for a,b in zip(md['observations']['right']['frames'],md['observations']['neutral']['frames'])
        if (a['x'],a['y'])!=(b['x'],b['y'])),None)
    paths=[Path(__file__),base/'report.json',original]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
