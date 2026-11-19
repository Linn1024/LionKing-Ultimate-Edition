"""Preserve full Pride route PCM and exercise paced supported mixed audio."""
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
    ap=argparse.ArgumentParser();ap.add_argument('--device',action='store_true');args=ap.parse_args()
    base=ROOT/'build/pride-audio-prime30';build=base/'build-report.json';bound(build)
    narrow=ROOT/'build/pride-restart-difficulty25/completion2/report.json';a=bound(narrow)
    wide=ROOT/'build/pride-restart-difficulty25/wide-completion/report.json';b=bound(wide)
    out=base/('routes-device' if args.device else 'routes');out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    labels=['256-md'] if args.device else ['256-snes','256-snes-lle','256-md','256-md-lle','320-md','320-md-lle']
    for label in labels:
        old=b if label.startswith('320') else a
        old_key=('lle' if label.endswith('-lle') else 'aot') if label.startswith('320') else label
        template=old['commands'][old_key];folder=out/label;folder.mkdir();cmd=template.copy();cmd[0]=str(base/'player.exe')
        for flag,value in [('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        env=dict(clean,TLK_FINAL_MD_ART='1')
        if args.device:
            for flag in ('--no-audio','--no-pace'):
                if flag in cmd:cmd.remove(flag)
            env.update(SDL_AUDIO_DRIVER='wasapi',TLK_AUDIO_QUEUE_TRACE=str(folder/'queue.csv'))
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[label]=cmd;checks[label+'_exit']=result.returncode==0
        scene=json.loads((folder/'scene.json').read_text());checks[label+'_next_level']=scene['level']==1
        ref=Path(template[template.index('--dump-window')+1]).parent
        checks[label+'_guest_preserved']=hashes(folder/'run.log')==hashes(ref/'run.log')
        checks[label+'_client_preserved']=pixels(folder/'window.png')==pixels(ref/'window.png')
        audio=pcm(folder/'audio.wav');reference=pcm(ref/'audio.wav')
        if not args.device:checks[label+'_complete_pcm_preserved']=audio==reference
        else:
            text=(folder/'run.log').read_text();stats=re.search(r'audio_underruns=(\d+) late_resyncs=(\d+)',text)
            with (folder/'queue.csv').open() as stream:rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(stream)]
            checks[label+'_opened_device']='continuing without sound' not in text and stats is not None
            checks[label+'_no_queue_underruns']=stats is not None and int(stats[1])==0
            checks[label+'_no_missing_requests']=rows[-1]['missing_calls']==0
            checks[label+'_audible_servo_budget']=any(audio) and abs(len(audio)-len(reference))<=len(reference)*.005+8
            observations[label]=dict(underruns=int(stats[1]) if stats else None,late_resyncs=int(stats[2]) if stats else None,
                                     missing_calls=rows[-1]['missing_calls'],device_samples=len(audio)//4,offline_samples=len(reference)//4)
        print(label,'level',scene['level'],'checks',all(v for k,v in checks.items() if k.startswith(label+'_')),flush=True)
    paths=[Path(__file__),build,narrow,wide]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                actual_device=args.device,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
