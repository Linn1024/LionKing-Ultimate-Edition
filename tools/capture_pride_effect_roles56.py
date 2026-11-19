"""Capture the current HUD and generated caption roles in real Windows clients."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-effect-observer56';out=base/'public-windows';out.mkdir()
    source=ROOT/'build/pride-checkpoint-capability53/completion/report.json';prior=bound(source)
    observer=base/'verification/report.json';assert bound(observer)['result']=='PASS'
    template=prior['commands']['aot'].copy();i=template.index('--no-pace');del template[i]
    i=template.index('--hash-at');del template[i:i+2]
    i=template.index('--dump-window');del template[i:i+2]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    USER32.SetProcessDPIAware();commands={};checks={};snapshots={}
    def run(choice):
        folder=out/choice;folder.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]='1150'
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        profile=Path(template[template.index('--resource-profile')+1]).read_text()
        profile+='\ngraphics.titles.pride_lands = '+choice+'\n'
        (folder/'resources.ini').write_text(profile);cmd+=['--hash-at','1060,1070,1080,1090,1100']
        commands[choice]=cmd;trace=folder/'tree.jsonl';env=dict(clean,TLK_SOFT_TREE_LOG=str(trace));hwnd=None
        with (folder/'run.log').open('wb') as log:
            proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                deadline=time.monotonic()+90
                while proc.poll() is None and time.monotonic()<deadline:
                    row=latest(trace)
                    if row and row['field']>=1070:
                        hwnd=window_for(proc.pid)
                        if hwnd:break
                    time.sleep(.005)
                assert hwnd,(choice,'no current opening window')
                before=latest(trace);capture_client(hwnd,folder/'game.png');after=latest(trace)
                snapshots[choice]=dict(before=before,after=after)
                selected=lambda key:next(r for r in before['choices'] if r[0]==key)[-1]
                checks[choice+'_ordinary_opening']=before['level']==0 and before['descriptor']==0xc00387 and before['health']>0
                checks[choice+'_capture_within_opening_interval']=1070<=before['field']<=after['field']<=1100
                checks[choice+'_hud_frames_md']=selected('graphics.hud.frames')==2
                checks[choice+'_caption_selection_applied']=all(selected('graphics.titles.pride_lands.'+part)==(2 if choice=='md' else 1) for part in ('frames','palette','position','duration'))
                proc.wait(timeout=90);checks[choice+'_clean_exit']=proc.returncode==0
            finally:
                if proc.poll() is None:
                    if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        print(choice,'captured',snapshots[choice]['before']['field'],flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,('md','snes')))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda choice:re.findall(pattern,(out/choice/'run.log').read_text())
    checks['five_original_guest_fields_unchanged']=len(hashes('md'))==5 and hashes('md')==hashes('snes')
    checks['full_pcm_unchanged']=digest(out/'md/audio.wav')==digest(out/'snes/audio.wav')
    checks['raw_scene_unchanged']=digest(out/'md/scene.json')==digest(out/'snes/scene.json')
    paths=[Path(__file__),source,observer,ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,snapshots=snapshots,
                actual_public_binary=True,operates_only_own_child_windows=True,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
