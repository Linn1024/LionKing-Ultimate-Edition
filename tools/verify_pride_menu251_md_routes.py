"""Maintained226 MD final timing: independent art, all menu outcomes/both widths."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm

build_path=ROOT/'build/pride-menu226-integrated/build-report.json';build=bound(build_path)
continue_path=ROOT/'build/pride-menu210-continue/report.json';cont=bound(continue_path)
over_path=ROOT/'build/pride-menu198-clocks/report.json';over=bound(over_path)
out=ROOT/'build/pride-menu251-md-routes';out.mkdir()
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
clean['SDL_VIDEODRIVER']='dummy'
pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
commands={};checks={}
def case(width,route):
    local={}
    for mode in ('control','aot','lle'):
        name=f'{width}-{route}-{mode}';folder=out/name;folder.mkdir()
        cmd=(over['commands']['snes-aot'] if route=='gameover' else cont['commands'][route]).copy()
        cmd[0]=str(build_path.parent/'player.exe')
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
            text=Path(cmd[cmd.index(flag)+1]).read_text()
            if flag=='--resource-profile':
                text+='display.viewport = '+('md' if width==320 else 'snes')+'\n'
                text+='gameplay.levels.pride_lands.final_life = md\n'
                text+='graphics.pride_final_menu = '+('snes' if mode=='control' else 'md')+'\n'
            (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):
            cmd[cmd.index(flag)+1]=str(folder/file)
        if mode=='lle':cmd.append('--lle')
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        local[name+'_exit']=rc==0
        if rc!=0: return local
        if mode!='control':
            control=out/f'{width}-{route}-control'
            actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(control/'run.log').read_text())
            local[name+'_all2501_guest_fields']=len(actual)==2501 and actual==expected
            local[name+'_whole_PCM']=pcm(folder/'audio.wav')==pcm(control/'audio.wav')
            local[name+'_scene']=(folder/'scene.json').read_bytes()==(control/'scene.json').read_bytes()
            same=digest(folder/'window.png')==digest(control/'window.png')
            local[name+'_endpoint_art_or_retirement']=(not same) if route=='idle' else same
            if mode=='lle':local[name+'_mode_client']=digest(folder/'window.png')==digest(out/f'{width}-{route}-aot/window.png')
        # Preserve the complete evidence using transparent compression after exit.
        subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(folder/'audio.wav')],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        print(name,rc,flush=True)
    return local
with ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(case,width,route) for width in (256,320) for route in ('idle','yes','no','gameover')]
    for future in futures:
        checks.update(future.result())
        (out/'partial.json').write_text(json.dumps(checks,indent=2)+'\n')
paths=[Path(__file__),build_path,continue_path,over_path]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) and len(commands)==24 else 'FAIL',checks=checks,commands=commands,
    scope='Maintained226 MD final-life timing at256/320: idle, YES, NO, zero-credit Game Over. Independent resource-selected MD art AOT/LLE versus same-width same-timing SNES-art controls: all2501 full guest samples, whole PCM, scene, endpoint ownership/retirement. No original full-game equivalence or real-window proof from this headless matrix.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
