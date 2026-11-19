"""Qualify output diagnostics on completed current-candidate lifecycle captures."""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_audio_state import wav_data


def main():
    base=ROOT/'build/pride-music-observer63';bp=base/'build-report.json';build=bound(bp)
    source=ROOT/'build/pride-music-output62/lifecycle/report.json';prior=bound(source)
    out=base/'verification';out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    cases=[('revival','aot',4500),('hard','aot',2850),('continue','aot',4450),('continue','lle',4450)]
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    def run(item):
        route,mode,start=item;name=route+'-'+mode;folder=out/name;folder.mkdir();cmd=prior['commands'][route+'-loaded'].copy();cmd[0]=str(base/'player.exe')
        if mode=='lle':cmd+=['--lle']
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        commands[name]=cmd
        env=dict(clean,TLK_MUSIC_OUTPUT_STATS=str(folder/'output.csv'),TLK_MUSIC_OUTPUT_EDGE=str(folder/'edge.csv'),TLK_SEMANTIC_OWNER_TRACE=str(folder/'owner.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        profile='both' if route=='revival' else 'all';reference=source.parent/f'{route}-{profile}-{mode}'
        checks[name+'_exit']=rc==0
        checks[name+'_every_continued_guest_field_neutral']=hashes(folder)==[r for r in hashes(reference) if int(r[0])>start]
        for file in ('scene.json','window.png'):checks[name+'_'+file+'_neutral']=digest(folder/file)==digest(reference/file)
        whole=wav_data(reference/'audio.wav');tail=wav_data(folder/'audio.wav')
        checks[name+'_whole_pcm_neutral']=bool(tail) and whole[-len(tail):]==tail
        totals={}
        for row in csv.DictReader((folder/'output.csv').open()):
            scene=f'{int(row["scene"]):06x}';entry=totals.setdefault(scene,dict(calls=0,filtered=0,echo_nonzero=0))
            for key in entry:entry[key]+=int(row[key])
        checks[name+'_no_echo_blocked_samples']=all(row['echo_nonzero']==0 for row in totals.values())
        observations[name]=totals
        print(name,rc,totals,flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,cases))
    checks['actual_music_filtered_in_all_three_contexts']=all(any(values.get(scene,{}).get('filtered',0)>0 for values in observations.values()) for scene in ('c00387','c0080d','c0057b'))
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                original_continue_pcm_failure_not_reclassified=True,read_only_observer=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
