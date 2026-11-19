"""Private native-timing MD Continue output, full guest/audio preservation."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm
reference=ROOT/'build/pride-menu210-continue/report.json';ref=bound(reference);assert ref['result']=='CAPTURED'
build=ROOT/'build/pride-menu215-native-art/build-report.json';bound(build)
out=ROOT/'build/pride-menu216-continue';out.mkdir();checks={};commands={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
for case in ('idle','yes','no'):
    for mode in ('aot','lle'):
        name=case+'-'+mode;folder=out/name;folder.mkdir()
        cmd=ref['commands'][case].copy();cmd[0]=str(build.parent/'player.exe')
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/file)
        if mode=='lle':cmd.append('--lle')
        env=dict(clean,SDL_VIDEODRIVER='dummy',TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU215='1',TLK_MENU197=str(folder/'menu.csv'))
        with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        commands[name]=cmd;checks[name+'_exit']=rc==0
        assert rc==0,(name,rc)
        control=reference.parent/case
        actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(control/'run.log').read_text())
        checks[name+'_all2501_guest_samples_exact']=actual==expected and len(actual)==2501
        checks[name+'_whole_native_pcm_exact']=pcm(folder/'audio.wav')==pcm(control/'audio.wav')
        checks[name+'_native_callback_clocks_exact']=(folder/'menu.csv').read_bytes()==(control/'menu.csv').read_bytes()
        checks[name+'_guest_scene_endpoint_exact']=(folder/'scene.json').read_bytes()==(control/'scene.json').read_bytes()
        checks[name+'_expected_art_ownership_at_endpoint']=(digest(folder/'window.png')!=digest(control/'window.png')) if case=='idle' else digest(folder/'window.png')==digest(control/'window.png')
        if mode=='lle':checks[case+'_mode_client_exact']=digest(folder/'window.png')==digest(out/(case+'-aot')/'window.png')
        print(name,{k:v for k,v in checks.items() if k.startswith(name+'_')},flush=True)
        (out/'partial.json').write_text(json.dumps(checks,indent=2)+'\n')
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Native timing idle Continue, YES and NO, selected installed MD artwork. Fresh ordinary routes, all2501 guest samples, whole native PCM/callback lifecycles, mode parity and ownership endpoints. Visual phases separate; no public/320/save/source-switch claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
