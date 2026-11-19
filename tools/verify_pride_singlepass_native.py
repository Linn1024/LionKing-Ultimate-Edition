"""Verify the ordinary native canvas and menus, without forced mixed capture."""
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import read_rows
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-singlepass/plain-native';build_path=base/'build-report.json';build=bound(build_path);binary=base/'native.exe';assert digest(binary)==build['binary_sha256']
    prior=ROOT/'build/pride-reset/fixed4';prior_path=prior/'build-report.json';old=bound(prior_path);before=prior/'native-sdl.exe';assert digest(before)==old['runs']['sdl']['binary_sha256']
    out=base/'verified';out.mkdir();profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n');tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={};checks={};count=0
    for mode,menu,gl in (('aot',False,True),('lle',False,True),('aot',True,True),('aot',True,False)):
        case=mode+('-menu' if menu else '-play')+('-gl' if gl else '-sdl');folders=[];end=2001 if menu else 3000
        for variant,exe in (('before',before),('after',binary)):
            folder=out/case/variant;folder.mkdir(parents=True);folders.append(folder);config=folder/'host.ini';config.write_text(f'opengl = {int(gl)}\nscale = 2\n')
            cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--config',config,'--input',tape,'--frames',end+int(menu),'--speedrun','practice','--no-audio','--no-record','--no-pace','--dump-window',folder/'window.png','--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,end+1)))]
            if mode=='lle':cmd+=['--lle']
            if menu:cmd+=['--menu-at',end,'--menu-page','resources']
            commands[case+'/'+variant]=list(map(str,cmd))
            import os
            env=os.environ.copy();env['TLK_SINGLEPASS_LOG']=str(folder/'presents.csv')
            with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[case+'/'+variant],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
            assert not r.returncode,(case,variant,r.returncode)
        a,b=folders;pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)';rows=lambda f:re.findall(pattern,(f/'run.log').read_text())
        checks[case+'/every_field']=rows(a)==rows(b) and len(rows(b))==end
        checks[case+'/whole_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[case+'/complete_pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
        presents=read_rows(b/'presents.csv');count+=len(presents)
        checks[case+'/one_pass']=bool(presents) and all(r['toast_calls']=='1' for r in presents)
        checks[case+'/menu_state']=any(r['menu']=='1' for r in presents)==menu
        print(case,'compared',flush=True)
    paths=[Path(__file__),build_path,prior_path,tape,ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_live_error_ui.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,presentations=count,commands=commands,binary_sha256=digest(binary),
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
