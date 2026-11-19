"""Maintained music filter: exact gameplay/PCM and current-build resumes."""
from concurrent.futures import ThreadPoolExecutor
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
    base=ROOT/'build/pride-music-output62';bp=base/'build-report.json';build=bound(bp)
    source=ROOT/'build/pride-music-output61/verification/report.json';prior=bound(source);assert prior['result']=='PASS'
    out=base/'verification';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(name):
        folder=out/name;folder.mkdir();cmd=prior['commands'][name].copy();cmd[0]=str(base/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        cmd+=['--save-at','4000',str(folder/'current.state')];commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0
        loaded=folder/'loaded';loaded.mkdir();resume=cmd.copy();index=resume.index('--save-at');del resume[index:index+3]
        resume+=['--load',str(folder/'current.state')]
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:resume[resume.index(flag)+1]=str(loaded/file)
        commands[name+'-loaded']=resume
        with (loaded/'run.log').open('wb') as log:rc=subprocess.run(resume,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_current_resume_exit']=rc==0
        print(name,'full/resume complete',flush=True);return name,folder
    names=[choice+'-'+mode for choice in ('native','music') for mode in ('aot','lle')]
    with ThreadPoolExecutor(max_workers=3) as pool:runs=dict(pool.map(run,names))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    for name,folder in runs.items():
        reference=source.parent/name;loaded=folder/'loaded'
        checks[name+'_every4600_guest_field_matches_qualified_prototype']=len(hashes(folder))==4600 and hashes(folder)==hashes(reference)
        for file in ('audio.wav','window.png','scene.json'):checks[name+'_'+file+'_matches_prototype']=digest(folder/file)==digest(reference/file)
        checks[name+'_every600_resumed_guest_field_exact']=hashes(loaded)==[r for r in hashes(folder) if int(r[0])>4000] and len(hashes(loaded))==600
        tail=wav_data(loaded/'audio.wav');whole=wav_data(folder/'audio.wav')
        checks[name+'_whole_resumed_pcm_tail_exact']=bool(tail) and whole[-len(tail):]==tail
        for file in ('window.png','scene.json'):checks[name+'_loaded_'+file+'_exact']=digest(folder/file)==digest(loaded/file)
    for choice in ('native','music'):
        for phase in ('','loaded'):
            a=runs[choice+'-aot']/phase;b=runs[choice+'-lle']/phase
            checks[choice+'_'+phase+'_whole_pcm_mode_parity']=digest(a/'audio.wav')==digest(b/'audio.wav')
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                current_build_resumes_only=True,public_preview_unchanged=True,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
