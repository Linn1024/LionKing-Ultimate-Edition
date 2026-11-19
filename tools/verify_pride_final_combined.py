"""Exercise combined source saves on ordinary power-on hard-difficulty play."""
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
    out=base/'verification';out.mkdir();checks={};commands={};observations={}
    cfg=out/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\n')
    tape=ROOT/'build/pride-game-over-music/hard.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    def run(label,end,save=None,load=None):
        folder=out/label;folder.mkdir()
        cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--config',cfg,'--input',tape,'--frames',end,'--no-pace','--no-audio','--no-record',
            '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json','--wav',folder/'audio.wav','--wav-seconds',120]
        if save:cmd+=['--save-at',save,folder/'saved.state']
        if load:cmd+=['--load',load]
        with (folder/'run.log').open('wb') as log:
            process=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        commands[label]=list(map(str,cmd));return folder,process.returncode
    for label,field in [('ordinary',1500),('final-fade',2376)]:
        direct,exit_code=run(label,field+1,save=field)
        checks[label+'_exit']=exit_code==0
        saved=direct/'saved.state';checks[label+'_save_written']=saved.is_file()
        if not saved.is_file():
            observations[label]=dict(save_error=(direct/'run.log').read_text()[-1800:]);continue
        raw=saved.read_bytes();inner=raw[96:96+struct.unpack_from('<I',raw,20)[0]]
        checks[label+'_combined_version']=raw[:8]==b'TLKFSV01' and struct.unpack_from('<I',raw,8)[0]==2
        checks[label+'_ordinary_backend']=inner[:8]==b'PRPRAC01'
        observations[label]=dict(backend=inner[:8].decode(),field=struct.unpack_from('<I',raw,32)[0])
        resumed,resume_exit=run(label+'-resumed',field+1,load=saved)
        checks[label+'_resume_exit']=resume_exit==0
        if resume_exit:continue
        checks[label+'_resume_guest']=hashes(resumed/'run.log')==hashes(direct/'run.log')
        checks[label+'_resume_client']=pixels(resumed/'window.png')==pixels(direct/'window.png')
        tail=pcm(resumed/'audio.wav');checks[label+'_resume_pcm']=bool(tail) and tail==pcm(direct/'audio.wav')[-len(tail):]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),build,tape]},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
