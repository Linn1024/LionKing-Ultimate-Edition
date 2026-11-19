"""Actual resource-selected MD menu art with independently selected MD timing."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_pride_final_scene_runtime import pcm
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride-menu227-integrated-windows/report.json';ref=bound(reference)
build=ROOT/'build/pride-menu226-integrated/build-report.json';bound(build)
assert shutil.disk_usage(ROOT).free>30*1024*1024 and shutil.disk_usage('G:/').free>30*1024*1024,'Need30MiB each for split control/live WAV capture'
out=ROOT/'build/pride-menu240-md-timing';out.mkdir();checks={};observations={};commands={}
target=Path('G:/lionKing-menu240-control-'+uuid.uuid4().hex);assert not target.exists();target.mkdir()
link=out/'control';quote=lambda p:"'"+str(p).replace("'","''")+"'"
subprocess.run(['powershell.exe','-NoProfile','-Command','New-Item -ItemType Junction -Path '+quote(link)+' -Target '+quote(target)+' | Out-Null'],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
assert link.resolve()==target.resolve()
(out/'control-storage.json').write_text(json.dumps(dict(target=str(target),scope='Owned control WAV/logs accessed beneath ignored build; no existing data moved.'),indent=2)+'\n')
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for mode in ('control','selected'):
    folder=out/mode
    if mode!='control':folder.mkdir()
    cmd=ref['command'].copy()
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
        text=Path(cmd[cmd.index(flag)+1]).read_text()
        if flag=='--resource-profile':
            if mode=='control':text=text.replace('graphics.pride_final_menu = md','graphics.pride_final_menu = snes')
            text+='gameplay.levels.pride_lands.final_life = md\n'
        (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
    cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','120'];commands[mode]=cmd
    if mode=='control':
        with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=f,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks['same_timing_control_exit']=rc==0;assert rc==0,rc
        print('control exit',rc,flush=True);continue
    USER32.SetProcessDPIAware();hwnd=None;reader=None
    with (folder/'run.log').open('wb') as f:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=clean,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            reader=PlayerRead(Path(cmd[0]),proc.pid)
            def current():
                row=reader.snapshot();row.update(entry=reader.value('final_scene_entry'),age=reader.value('final_scene_age'),
                    confirmed_md=int.from_bytes(reader.read(reader.base+reader.symbols['_continue_transition'],8),'little'),
                    confirmed_credits=reader.value('final_menu_confirmed_credits'))
                return row
            for name,field in [('ready',4400),('hold',4510),('exit-pose',4570),('retained-credit',4680),('resumed-level',5000)]:
                deadline=time.monotonic()+150;row=None
                while proc.poll() is None and time.monotonic()<deadline:
                    r=current()
                    if r['field']>=field:
                        row=r;hwnd=window_for(proc.pid)
                        if hwnd:break
                    time.sleep(.003)
                assert row and hwnd,(name,proc.poll())
                capture_client(hwnd,folder/(name+'.png'));observations[name]=dict(before=row,after=current())
                checks[name+'_independent_md_timing_and_art']=row['art_mode']==1 and row['transition_mode']==1 and row['active']==0 and field<=row['field']<field+10
                print(name,row['field'],'entry',row['entry'],'confirm',row['confirmed_md'],flush=True)
        finally:
            if reader:reader.close()
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['selected_clean_exit']=proc.returncode==0
pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
actual=re.findall(pattern,(out/'selected/run.log').read_text());expected=re.findall(pattern,(out/'control/run.log').read_text())
checks['same_timing_all_observed_guest_samples_exact']=len(actual)>1400 and actual==expected[:len(actual)]
a=pcm(out/'selected/audio.wav');b=pcm(out/'control/audio.wav')
checks['complete_captured_native_pcm_prefix_exact']=bool(a) and a==b[:len(a)]
checks['confirmed_counter_retained']=observations['retained-credit']['before']['confirmed_credits']==1
paths=[Path(__file__),reference,build,ROOT/'tools/pride_process_read.py',ROOT/'tools/windows_capture.py']
files={p for p in out.rglob('*') if p.is_file()};files.update(p for p in link.iterdir() if p.is_file())
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
    scope='Current226 actual320 resource-selected MD menu art with independently selected MD final-life timing. Same-timing SNES-art control preserves observed guest and whole captured native PCM prefix; actual Windows bright menu/retirement views. Pixels separate; not a full source matrix/release claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in sorted(files)}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
