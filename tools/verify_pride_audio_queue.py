"""Compare offline PCM/guest/client and paced Windows device queue telemetry."""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--player',default='build/pride-audio-queue27')
    ap.add_argument('--output',default='queue');ap.add_argument('--cases',default='title')
    ap.add_argument('--repeats',type=int,default=1);ap.add_argument('--require-priming',action='store_true')
    ap.add_argument('--lle',action='store_true');args=ap.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    title=ROOT/'build/pride-title-ready18/device/report.json';old=bound(title)
    fixtures=ROOT/'build/pride-restart-difficulty-fixtures/report.json';prepared=bound(fixtures)
    out=base/args.output;out.mkdir();checks={};commands={};observations={}
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\naudio = 1\naudio_rate = 48000\nvolume = 100\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for case in args.cases.split(','):
        if case=='title':template=old['command'].copy()
        elif case in ('boot','cold'):
            template=prepared['commands']['md-normal'].copy()
            if '--save-at' in template:i=template.index('--save-at');del template[i:i+3]
            if case=='cold':
                i=template.index('--input');del template[i:i+2]
                template+=['--load',str(fixtures.parent/'md-normal/saved.state')]
                template[template.index('--frames')+1]='2600'
        else:raise ValueError(case)
        for flag in ('--no-audio','--no-pace'):
            if flag in template:template.remove(flag)
        if args.lle and '--lle' not in template:template.append('--lle')
        folders={}
        for mode in ['reference','offline']+['device'+str(n) for n in range(args.repeats)]:
            folder=out/(case+'-'+mode);folder.mkdir();folders[mode]=folder
            cmd=template.copy();cmd[0]=str(ROOT/'build/pride-restart-difficulty25/player.exe' if mode=='reference' else base/'player.exe')
            for flag,value in [('--config',config),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
            device=mode.startswith('device')
            if not device:cmd+=['--no-audio','--no-pace']
            env=dict(clean,TLK_FINAL_MD_ART='1')
            if device:env.update(SDL_AUDIO_DRIVER='wasapi',TLK_AUDIO_QUEUE_TRACE=str(folder/'queue.csv'))
            with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
            label=folder.name;commands[label]=cmd;checks[label+'_exit']=r.returncode==0
            if mode=='reference':continue
            ref=folders['reference'];checks[label+'_guest']=hashes(folder/'run.log')==hashes(ref/'run.log')
            checks[label+'_client']=pixels(folder/'window.png')==pixels(ref/'window.png')
            a=pcm(folder/'audio.wav');b=pcm(ref/'audio.wav')
            if not device:checks[label+'_full_pcm']=a==b;continue
            log=(folder/'run.log').read_text();stats=re.search(r'audio_underruns=(\d+) late_resyncs=(\d+)',log)
            checks[label+'_device_opened']=stats is not None and 'continuing without sound' not in log
            checks[label+'_audible_pcm']=any(a) and abs(len(a)-len(b))<=len(b)*.005+8
            with (folder/'queue.csv').open() as stream:rows=[{k:int(v) for k,v in row.items()} for row in csv.DictReader(stream)]
            observations[label]=dict(underruns=int(stats[1]),late_resyncs=int(stats[2]),
                queue_empty_fields=[r['frame'] for r in rows if r['queued_frames']==0],
                first_rows=rows[:12],last_row=rows[-1],device_samples=len(a)//4,offline_samples=len(b)//4)
            if args.require_priming:
                checks[label+'_no_queue_underruns']=int(stats[1])==0
                checks[label+'_primed_before_play']=any(r['paused']==1 and r['queued_frames']>0 for r in rows) and any(r['paused']==0 for r in rows)
                checks[label+'_no_missing_device_requests']=rows[-1]['missing_calls']==0
            print(label,observations[label]['underruns'],'underruns, missing calls',rows[-1]['missing_calls'],flush=True)
    paths=[Path(__file__),build,title,fixtures]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                zero_underruns_required=args.require_priming,device_offline_pcm_equality_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
