"""Compare resource-selected runtime against native and prior MD controls."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-launch';build_path=base/'build-report.json';build=bound(build_path);out=base/'probe';out.mkdir();checks={};commands={};results={}
    plain_path=ROOT/'build/pride-tree-help2/plain-native/build-report.json';plain=bound(plain_path)
    md_path=ROOT/'build/pride-save-identity2/build-report.json';md_build=bound(md_path)
    template=ROOT/'build/pride-source-live/seeded/resources.ini';tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for case,mode,graphics,md_present in (('native-aot','aot',False,False),('native-lle','lle',False,False),('mixed-native','aot',True,True),('md-death','lle',True,True)):
        root=out/case;root.mkdir();death=case=='md-death';profiles={}
        for name in ('before','after'):
            profile=root/(name+'.ini');profile.write_bytes(template.read_bytes() if graphics else b'schema = 1\ngame = snes\n')
            if name=='after' and death:
                with profile.open('ab') as f:f.write(b'gameplay.levels.pride_lands.health_death = md\n')
            profiles[name]=profile
        for name in ('before','after'):
            folder=root/name;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
            exe=base/'player.exe' if name=='after' else ROOT/('build/pride-save-identity2/a.exe' if death else 'build/pride-tree-help2/plain-native/native.exe')
            expected=build['binary_sha256'] if name=='after' else (md_build['runs']['a']['binary_sha256'] if death else plain['binary_sha256']);assert digest(exe)==expected
            cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md' if md_present else root/'missing.md','--resource-profile',profiles[name],
                 '--config',config,'--input',tape,'--frames',3000,'--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
                 '--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,3001)))]
            if mode=='lle':cmd+=['--lle']
            commands[case+'/'+name]=list(map(str,cmd))
            env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
            if name=='before' and death:env=environment(folder)
            with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[case+'/'+name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
            results[case+'/'+name]=r.returncode;checks[case+'/'+name+'/exit']=r.returncode==0
            for file in folder.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(file)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
        a,b=root/'before',root/'after';rows=lambda f:re.findall(pattern,(f/'run.log').read_text())
        checks[case+'/all_guest_fields']=rows(a)==rows(b) and len(rows(b))==3000
        complete=all((f/name).exists() for f in (a,b) for name in ('window.png','guest.png','audio.wav'))
        checks[case+'/complete_pcm']=complete and wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
        checks[case+'/whole_client']=complete and pixels(a/'window.png')==pixels(b/'window.png')
        checks[case+'/whole_guest']=complete and pixels(a/'guest.png')==pixels(b/'guest.png')
        print(case,'exits',results[case+'/before'],results[case+'/after'],'failures',[k for k,v in checks.items() if not v and k.startswith(case+'/')],flush=True)
    paths=[Path(__file__),build_path,plain_path,md_path,template,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,exit_codes=results,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)


if __name__=='__main__':main()
