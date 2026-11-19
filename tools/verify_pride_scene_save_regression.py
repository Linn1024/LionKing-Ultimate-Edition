"""Keep the preceding native/mixed/owned behavior exact after save dispatch."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-launch3';build_path=base/'build-report.json';build=bound(build_path)
    previous=ROOT/'build/pride-launch2/probe/report.json';old=bound(previous);assert old['result']=='PASS'
    out=base/'regression';out.mkdir();checks={};commands={};count=0
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for case in ('native-aot','native-lle','mixed-native','md-death'):
        folder=out/case;folder.mkdir();cmd=list(old['commands'][case+'/after']);cmd[0]=str(base/'player.exe')
        for flag,name in (('--config','host.ini'),('--wav','audio.wav'),('--dump-window','window.png'),('--dump-png','guest.png')):
            cmd[cmd.index(flag)+1]=str(folder/name)
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        commands[case]=cmd
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        before=previous.parent/case/'after'
        actual=re.findall(pattern,(folder/'run.log').read_text());count+=len(actual)
        checks[case+'/exit']=not r.returncode
        checks[case+'/every_field']=len(actual)==3000 and actual==re.findall(pattern,(before/'run.log').read_text())
        checks[case+'/pcm']=wav_data(folder/'audio.wav')==wav_data(before/'audio.wav')
        checks[case+'/guest']=pixels(folder/'guest.png')==pixels(before/'guest.png')
        checks[case+'/client']=pixels(folder/'window.png')==pixels(before/'window.png')
        print(case,[k for k,v in checks.items() if not v],flush=True)
    paths=[Path(__file__),build_path,previous,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,native_fields_compared=count,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
