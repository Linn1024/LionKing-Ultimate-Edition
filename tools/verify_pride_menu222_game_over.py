"""Regress215 native-timing zero-credit Game Over at both viewport widths."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm
reference=ROOT/'build/pride-menu198-clocks/report.json';ref=bound(reference)
candidate=ROOT/'build/pride-menu215-native-art/build-report.json';bound(candidate)
public=ROOT/'build/pride-hyena-entrance139/build-report.json';bound(public)
out=ROOT/'build/pride-menu222-game-over';out.mkdir();checks={};commands={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
for width in (256,320):
    control=reference.parent/'snes/aot'
    for mode in (('aot','lle') if width==256 else ('control','aot','lle')):
        name=str(width)+'-'+mode;folder=out/name;folder.mkdir()
        cmd=ref['commands']['snes-aot'].copy();cmd[0]=str((public if mode=='control' else candidate).parent/'player.exe')
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
            text=Path(cmd[cmd.index(flag)+1]).read_text()
            if flag=='--resource-profile' and width==320:text+='display.viewport = md\n'
            (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/file)
        if mode=='lle':cmd.append('--lle')
        env=dict(clean,SDL_VIDEODRIVER='dummy')
        if mode!='control':env.update(TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU215='1',TLK_MENU197=str(folder/'menu.csv'))
        with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        commands[name]=cmd;checks[name+'_exit']=rc==0;assert rc==0,(name,rc)
        if mode=='control':control=folder
        else:
            actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(control/'run.log').read_text())
            checks[name+'_all2501_samewidth_guest_samples_exact']=actual==expected and len(actual)==2501
            checks[name+'_whole_samewidth_native_pcm_exact']=pcm(folder/'audio.wav')==pcm(control/'audio.wav')
            checks[name+'_later_client_native_after_retirement']=digest(folder/'window.png')==digest(control/'window.png')
            checks[name+'_scene_exact']=(folder/'scene.json').read_bytes()==(control/'scene.json').read_bytes()
            if mode=='lle':checks[str(width)+'_mode_client_exact']=digest(folder/'window.png')==digest(out/(str(width)+'-aot')/'window.png')
        print(name,'exit',rc,flush=True)
        (out/'partial.json').write_text(json.dumps(checks,indent=2)+'\n')
paths=[Path(__file__),reference,candidate,public]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Private215 zero-credit native Game Over at256/320. Actual same-width public controls, guest/wholePCM/scene/end-client/mode preservation. During-menu actual Windows/pixels separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
