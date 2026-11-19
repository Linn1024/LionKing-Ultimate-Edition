"""Capture two visibly different resource editors using the same unmodified save."""
import json
from pathlib import Path
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-save-identity2';build_path=base/'build-report.json';build=bound(build_path)
    author=base/'verified/md/author-a';state=author/'tlk_practice_restart.state';before=digest(state)
    profile=base/'verified/md/resources.ini';out=base/'ui';out.mkdir();commands={};images={};checks={}
    for variant in ('a','b'):
        folder=out/variant;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        exe=base/(variant+'.exe');assert digest(exe)==build['runs'][variant]['binary_sha256']
        tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
        cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,
             '--load',state,'--input',tape,'--frames',1601,'--lle','--no-audio','--no-record','--no-pace','--speedrun','practice','--menu-at',1600,'--menu-page','resources']
        commands[variant]=list(map(str,cmd));env=environment(folder);trace=folder/'presents.jsonl';env['TLK_SOFT_TREE_LOG']=str(trace)
        with (folder/'run.log').open('wb') as log:
            proc=subprocess.Popen(commands[variant],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);deadline=time.monotonic()+90;hwnd=None
            try:
                while proc.poll() is None and time.monotonic()<deadline:
                    if not hwnd:hwnd=window_for(proc.pid)
                    row=latest(trace)
                    if hwnd and row and row['field']==1600 and row['about']==2:break
                    time.sleep(.01)
                assert hwnd and proc.poll() is None and row['about']==2
                USER32.SetProcessDPIAware();capture_client(hwnd,folder/'client.png');images[variant]=pixels(folder/'client.png')
                checks[variant+'/actual_paused_editor']=row['menu']==1 and row['gl']==0 and row['dirty']==0
                assert USER32.PostMessageW(hwnd,0x100,0x7b,1);assert USER32.PostMessageW(hwnd,0x101,0x7b,0xc0000001)
                proc.wait(timeout=90);checks[variant+'/exit']=proc.returncode==0
            finally:
                if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    wa,ha,a=images['a'];wb,hb,b=images['b'];checks['actual_md_width']=wa==wb==640 and ha==hb==448
    changed=[(i%wa,i//wa) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    checks['visible_ui_change']=bool(changed)
    checks['only_title_pixels_change']=all(80<=x<352 and 8<=y<24 for x,y in changed)
    font=(ROOT/'engine/runner/tlk_font8x8.h').read_text();glyphs=[[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',row)] for row in re.findall(r'\{([^{}]+)\}',font)]
    for variant,title in (('a','VERSION RESOURCES'),('b','RESOURCE SOURCES')):
        w,h,rgb=images[variant]
        checks[variant+'/expected_title_glyphs']=all(rgb[(8+y*2+dy)*w+80+col*16+x*2+dx]==(255,255,255)
            for col,char in enumerate(title) for y,bits in enumerate(glyphs[ord(char)-32]) for x in range(8) if bits&(1<<x) for dy in (0,1) for dx in (0,1))
    checks['save_never_rewritten']=digest(state)==before
    paths=[Path(__file__),build_path,state,profile,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py',ROOT/'engine/runner/tlk_font8x8.h']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,title_pixels_changed=len(changed),
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
