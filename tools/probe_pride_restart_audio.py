"""Retain native audio/state evidence surrounding the observed cold-restart PCM drift."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import environment
from verify_pride_audio_state import wav_data


def main():
    base=ROOT/'build/pride-restart';reference=base/'final/windows/native-aot'
    report_path=reference/'report.json';report=json.loads(report_path.read_text())
    build_path=base/'build-report.json';build=json.loads(build_path.read_text())
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    out=base/'audio-diagnostic';out.mkdir(exist_ok=True);results=[]
    for field in (2761,2762):
        states={};audio={}
        for name in ('baseline','before'):
            folder=out/f'{field}-{name}';folder.mkdir(exist_ok=True)
            command=list(report['commands'][name]);command[command.index('--frames')+1]=str(field)
            for flag,filename in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):
                command[command.index(flag)+1]=str(folder/filename)
            command+=['--save-at',str(field),str(folder/'owned.state')]
            with (folder/'run.log').open('wb') as log:
                run=subprocess.run(command,cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=240)
            assert run.returncode==0,(field,name,run.returncode)
            states[name]=(folder/'owned.state').read_bytes();audio[name]=wav_data(folder/'audio.wav')
        a,b=states['baseline'],states['before'];at=next((n for n,(x,y) in enumerate(zip(a,b)) if x!=y),None)
        ai,bi=a.index(b'TLKAUD01'),b.index(b'TLKAUD01')
        aa,ba=a[ai:],b[bi:];ad=next((n for n,(x,y) in enumerate(zip(aa,ba)) if x!=y),None)
        x,y=audio['baseline'],audio['before'];prefix=len(y)-len(x)
        pd=next((n for n,(v,w) in enumerate(zip(x,y[prefix:])) if v!=w),None)
        result=dict(field=field,state_equal=a==b,first_state_difference=at,audio_history_offset=[ai,bi],
            first_audio_history_difference=ad,pcm_tail_equal=x==y[prefix:],first_pcm_difference=pd)
        results.append(result);print(result,flush=True)
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),report_path,build_path)}
    (out/'report.json').write_text(json.dumps(dict(result='OBSERVED',cases=results,source_sha256=sources,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')


if __name__=='__main__':main()
