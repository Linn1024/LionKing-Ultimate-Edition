"""Current215 native-timing Continue at320 against actual same-width139 controls."""
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
candidate=ROOT/'build/pride-menu215-native-art/build-report.json';bound(candidate)
public=ROOT/'build/pride-hyena-entrance139/build-report.json';bound(public)
out=ROOT/'build/pride-menu221-wide';out.mkdir();checks={};commands={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
for case in ('idle','yes','no'):
    for mode in ('control','aot','lle'):
        name=case+'-'+mode;folder=out/name;folder.mkdir()
        cmd=ref['commands'][case].copy();cmd[0]=str((public if mode=='control' else candidate).parent/'player.exe')
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
            text=Path(cmd[cmd.index(flag)+1]).read_text()
            if flag=='--resource-profile':text+='display.viewport = md\n'
            (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/file)
        if mode=='lle':cmd.append('--lle')
        env=dict(clean,SDL_VIDEODRIVER='dummy')
        if mode!='control':env.update(TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU215='1',TLK_MENU197=str(folder/'menu.csv'))
        with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;commands[name]=cmd;assert rc==0,(name,rc)
        if mode!='control':
            control=out/(case+'-control');actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(control/'run.log').read_text())
            checks[name+'_all2501_samewidth_guest_samples_exact']=actual==expected and len(actual)==2501
            checks[name+'_whole_samewidth_native_pcm_exact']=pcm(folder/'audio.wav')==pcm(control/'audio.wav')
            checks[name+'_samewidth_scene_exact']=(folder/'scene.json').read_bytes()==(control/'scene.json').read_bytes()
            checks[name+'_expected_art_endpoint_ownership']=(digest(folder/'window.png')!=digest(control/'window.png')) if case=='idle' else digest(folder/'window.png')==digest(control/'window.png')
            if mode=='lle':checks[case+'_mode_client_exact']=digest(folder/'window.png')==digest(out/(case+'-aot')/'window.png')
        print(name,'exit',rc,flush=True)
        (out/'partial.json').write_text(json.dumps(checks,indent=2)+'\n')
paths=[Path(__file__),reference,candidate,public]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Native timing Continue idle/YES/NO at320: actual same-width public139 controls versus private215 AOT/LLE, all2501 guest samples/whole PCM/scene and ownership endpoints. Actual Windows/pixels separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
