"""Verify combined sources across revival, final entry and cold menu continuation."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-final-combined';build=base/'build-report.json';bound(build)
    out=base/'lifecycle';out.mkdir();checks={};commands={};observations={}
    initial=base/'verification/report.json';templates=bound(initial)['commands']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    def run(label,route,end,save=None,load=None,lle=False):
        folder=out/label;folder.mkdir();cmd=templates['ordinary'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
        cmd[cmd.index('--input')+1]=str(ROOT/f'build/pride-game-over-music/{route}.tape')
        cmd[cmd.index('--frames')+1]=str(end)
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        if save:cmd+=['--save-at',str(save),str(folder/'saved.state')]
        if load:cmd+=['--load',str(load)]
        if lle:cmd+=['--lle']
        with (folder/'run.log').open('wb') as log:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        commands[label]=cmd;return folder,p.returncode
    for name,route,save,end,backend in [('ordinary-to-final','hard',1500,2500,b'PRPRAC01'),
        ('owned-to-revival','normal',1700,2050,b'PRHSAVE1'),('prior-revival-to-final-menu','normal',3800,3920,b'PRHSAVE1')]:
        direct,code=run(name,route,end,save=save);saved=direct/'saved.state'
        checks[name+'_direct_exit']=code==0;checks[name+'_save_exists']=saved.is_file()
        if not saved.is_file():observations[name]=(direct/'run.log').read_text()[-1600:];continue
        raw=saved.read_bytes();checks[name+'_backend']=raw[96:104]==backend
        observations[name]=dict(backend=raw[96:104].decode(),save_field=struct.unpack_from('<I',raw,32)[0])
        resumed,code=run(name+'-resumed',route,end,load=saved);checks[name+'_resume_exit']=code==0
        if code:observations[name]['resume_error']=(resumed/'run.log').read_text()[-1600:];continue
        checks[name+'_guest']=hashes(resumed/'run.log')==hashes(direct/'run.log')
        checks[name+'_client']=pixels(resumed/'window.png')==pixels(direct/'window.png')
        audio=pcm(resumed/'audio.wav');checks[name+'_pcm']=bool(audio) and audio==pcm(direct/'audio.wav')[-len(audio):]
        if name=='owned-to-revival':
            lle,code=run(name+'-lle',route,end,load=saved,lle=True)
            checks['owned_lle_exit']=code==0
            if not code:
                checks['owned_lle_guest']=hashes(lle/'run.log')==hashes(resumed/'run.log')
                checks['owned_lle_client']=pixels(lle/'window.png')==pixels(resumed/'window.png')
                checks['owned_lle_pcm']=pcm(lle/'audio.wav')==audio
    paths=[Path(__file__),build,initial,ROOT/'build/pride-game-over-music/normal.tape',ROOT/'build/pride-game-over-music/hard.tape']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
