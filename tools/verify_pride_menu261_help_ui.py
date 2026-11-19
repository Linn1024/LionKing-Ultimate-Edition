"""Check the corrected help through the actual Windows resource editor."""
import json
import os
from pathlib import Path
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from windows_capture import capture_client
from windows_json_pipe import JsonPipe

reference=ROOT/'build/pride-menu227-integrated-windows/report.json';ref=bound(reference)
build=ROOT/'build/pride-menu260-help/build-report.json';b=bound(build)
out=ROOT/'build/pride-menu261-help-ui';out.mkdir();checks={};snapshots={}
cmd=ref['command'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
cmd[cmd.index('--frames')+1]='2000';cmd[cmd.index('--hash-at')+1]='1500'
cmd+=['--menu-at','1500','--menu-page','resources']
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
USER32.SetProcessDPIAware();hwnd=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    def wait(predicate,seconds=120):
        deadline=time.monotonic()+seconds
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row and predicate(row):return row
            time.sleep(.008)
        raise AssertionError(('UI state missing',proc.poll(),trace.latest()))
    def key(vk):
        scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
        assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
        assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra)
        time.sleep(.055)
    try:
        row=wait(lambda r:r['field']==1500 and r['about']==2);hwnd=window_for(proc.pid);assert hwnd
        node='gameplay.levels.pride_lands.final_life';key(0x24)
        for _ in range(180):
            row=trace.latest();name=row['choices'][row['selected']][0]
            if name==node:break
            if name=='game' or node.startswith(name+'.'):key(0x27)
            key(0x28)
        assert name==node
        key(0x48);row=wait(lambda r:r['modal']==1);snapshots['first']=row
        checks['correct_complete_help']=('menu artwork, nonfinal revival and audio are selected independently' in row['help'] and 'later title-screen delay remains native' in row['help'] and 'native menu artwork and later title-screen delay remain' not in row['help'])
        checks['paused_at_requested_field']=row['field']==1500
        checks['help_has_multiple_pages']=row['pages']>1
        capture_client(hwnd,out/'help-first.png')
        key(0x22);after=wait(lambda r:r['page']==1);snapshots['second']=after
        capture_client(hwnd,out/'help-second.png')
        checks['help_pages_without_changing_selection']=after['selected']==row['selected'] and after['help']==row['help'] and after['field']==1500
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish();(out/'trace-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
checks['clean_exit']=proc.returncode==0
paths=[Path(__file__),reference,build,ROOT/'tools/windows_json_pipe.py',ROOT/'tools/windows_capture.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,snapshots=snapshots,command=cmd,
    scope='Current260 real Windows final-life resource scope text and paged help, paused without altering choices. Help-only build retains323/324226 inputs; this UI check is not a new full native75/All Bugs gate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
