"""Inventory current enabled cue rows, without counting inactive preprocessor branches."""
from collections import Counter
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-lizard-voice74';bp=base/'build-report.json';build=bound(bp)
    reference=base/'completion/report.json';prior=bound(reference);assert prior['result']=='PASS'
    out=ROOT/'build/pride-audio-dispatch75';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    pp=build['compiles']['audio'].copy();pp[pp.index('-c')]='-E';pp+=['-P']
    for flag,value in [('-o',out/'audio.i'),('-MT',out/'audio.obj'),('-MF',out/'audio.d')]:pp[pp.index(flag)+1]=str(value)
    with (out/'preprocess.log').open('wb') as log:subprocess.run(pp,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    text=(out/'audio.i').read_text();table=re.search(r'cues\[\]\s*=\s*\{(.*?)\n\};',text,re.S).group(1)
    cues=[]
    for resource,event,selector,value,actor,caller in re.findall(r'\{"([^"]+)",([^,]+),([^,]+),([^,]+),([^,]+),([^}]+)\}',table):
        cues.append(dict(resource=resource,event=int(event,0),selector=int(selector,0),value=int(value,0),actor=int(actor,0),caller=int(caller,0)))
    cmd=prior['commands']['aot'].copy()
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env.update(SDL_VIDEODRIVER='dummy',TLK_AUDIO_EVENTS=str(out/'events.csv'),TLK_MD_SOUND_COMMANDS=str(out/'driver.csv'))
    with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    groups=Counter();unmatched=Counter();other_scenes=Counter()
    for row in csv.DictReader((out/'events.csv').open()):
        event=int(row['event'],16)
        if event<=2:continue
        if row['level']!='0000' or row['descriptor'] not in ('0387','080d'):
            other_scenes[(row['descriptor'],f'{event:04x}')]+=1;continue
        raw=bytes.fromhex(row['stack']);offset=5 if row['return0']=='2d16' else 6 if row['return0']=='2d4d' else None
        caller=(int.from_bytes(raw[offset:offset+3],'little')+1)&0xffffff if offset is not None else 0
        actor=int(row['actor'],16)
        matches=tuple(c['resource'] for c in cues if c['event']==event and (c['actor']==1)==(actor==0xb213) and (not c['caller'] or c['caller']==caller))
        key=(event,caller,actor==0xb213,matches);groups[key]+=1
        if not matches:unmatched[key]+=1
    rows=lambda counter:[dict(event=k[0],caller=k[1],simba=k[2],candidate_resources=k[3],count=v) for k,v in sorted(counter.items())]
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    actual=re.findall(pattern,(out/'run.log').read_text());expected=re.findall(pattern,(reference.parent/'aot/run.log').read_text())
    lizard=[c for c in cues if c['resource']=='audio.effects.world.lizard'];hyena=[c for c in cues if c['resource']=='audio.effects.world.hyena_hurt']
    checks=dict(actual_capture_exit=rc==0,all6000_guest_fields_neutral=len(actual)==6000 and actual==expected,
                whole_pcm_neutral=digest(out/'audio.wav')==digest(reference.parent/'aot/audio.wav'),
                lizard_inactive_legacy_row_excluded=len(lizard)==1 and lizard[0]['selector']==0 and lizard[0]['caller']==0xc16527,
                hyena_inactive_legacy_row_excluded=len(hyena)==1 and hyena[0]['selector']==0 and hyena[0]['caller']==0xc1458d)
    for file in ('window.png','scene.json'):checks[file+'_neutral']=digest(out/file)==digest(reference.parent/'aot'/file)
    paths=[Path(__file__),bp,reference,out/'audio.i']
    report=dict(result='CURRENT_DISPATCH_INVENTORIED' if all(checks.values()) else 'FAIL',checks=checks,preprocess_command=pp,command=cmd,
                enabled_cue_rows=cues,observed_pride_dispatch=rows(groups),unmatched_pride_calls=rows(unmatched),
                other_scene_calls=[dict(scene=k[0],event=k[1],count=v) for k,v in sorted(other_scenes.items())],
                candidate_mapping_is_not_semantic_equivalence_proof=True,sun_owner_guard_not_reconstructed_from_event_csv=True,
                full_audio_or_first_level_completion_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,'unmatched',rows(unmatched),flush=True)


if __name__=='__main__':main()
