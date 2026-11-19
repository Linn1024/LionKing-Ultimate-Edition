"""Retain the actual6000-field320 completion after the host I/O-only change."""
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
    base=ROOT/'build/pride-rng-player3';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    previous=ROOT/'build/pride-rng-player2/completion-reference-unpaused2'
    rp=previous/'report.json';old=bound(rp)
    out=base/'completion-regression';out.mkdir();checks={};commands={}
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        cmd=old['commands'][f'320/{mode}'].copy();cmd[0]=str(base/'player.exe')
        for flag,name in (('--config','host.ini'),('--wav','route.wav'),('--dump-scene','scene.json'),('--dump-window','window.png'),('--dump-png','guest.png')):
            cmd[cmd.index(flag)+1]=str(folder/name)
        commands[mode]=cmd
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        before=previous/'320'/mode
        a=re.findall(pattern,(folder/'run.log').read_text());b=re.findall(pattern,(before/'run.log').read_text())
        checks[mode+'/exit']=result.returncode==0
        checks[mode+'/every_field']=len(a)==6000 and a==b
        checks[mode+'/full_pcm']=wav_data(folder/'route.wav')==wav_data(before/'route.wav')
        checks[mode+'/whole_client']=pixels(folder/'window.png')==pixels(before/'window.png')
        checks[mode+'/next_level']=json.loads((folder/'scene.json').read_text())['level']==1
        print(mode,[k for k,v in checks.items() if not v],flush=True)
    paths=[Path(__file__),bp,rp]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,compared_fields=12000,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],flush=True);assert all(checks.values())


if __name__=='__main__':main()
