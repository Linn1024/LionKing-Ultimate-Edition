"""Use the actual F12 tree to change title navigation from title and gameplay."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import time

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-title-navigation23');parser.add_argument('--reference',default='build/pride-title-navigation21');parser.add_argument('--output',default='switch2');args=parser.parse_args()
    base=ROOT/args.player;prior=ROOT/args.reference;bound(base/'build-report.json');reference=prior/'verification/report.json';old=bound(reference)
    out=base/args.output;out.mkdir();profile=out/'resources.ini';profile.write_bytes((prior/'verification/256-md.ini').read_bytes())
    seed=prior/'verification/256-selected/saved.state';trace=out/'tree.jsonl';node='gameplay.menus.title_navigation'
    cmd=old['commands']['256-selected'].copy();cmd.remove('--no-pace')
    cmd[0]=str(base/'player.exe')
    if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,value in [('--load',seed),('--frames',20000),('--config',out/'host.ini'),('--resource-profile',profile),
                       ('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json'),('--wav',out/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env.update(TLK_FINAL_MD_ART='1',TLK_SOFT_TREE_LOG=str(trace))
    checks={};snapshots={};hwnd=None
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait(predicate,timeout=25):
            end=time.monotonic()+timeout
            while proc.poll() is None and time.monotonic()<end:
                row=latest(trace)
                if row and predicate(row):return row
                time.sleep(.01)
            return None
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
            assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.06)
        try:
            USER32.SetProcessDPIAware();end=time.monotonic()+15
            while not hwnd and proc.poll() is None and time.monotonic()<end:hwnd=window_for(proc.pid);time.sleep(.01)
            assert hwnd and wait(lambda r:r['field']>=5094)
            for value,label in [(1,'snes-from-title'),(2,'md-from-gameplay')]:
                key(0x7b);assert wait(lambda r:r['about']==2,5);key(0x24)
                for _ in range(180):
                    row=latest(trace);selected=row['choices'][row['selected']][0]
                    if selected==node:break
                    if selected=='game' or node.startswith(selected+'.'):key(0x27)
                    key(0x28)
                checks[label+'_visible_node']=selected==node
                if selected!=node:break
                for _ in range(3):
                    if latest(trace)['choices'][row['selected']][1]==value:break
                    key(0x0d)
                snapshots[label]=latest(trace);capture_client(hwnd,out/(label+'.png'));key(0x71)
                restarted=wait(lambda r:not r['menu'] and r['field']<1000,5)
                checks[label+'_restarted']=restarted is not None
                checks[label+'_persisted']=node+' = '+('snes' if value==1 else 'md') in profile.read_text()
                if not restarted:break
                assert wait(lambda r:r['field']>=2000,30)
                after=latest(trace);snapshots[label+'-after']=after
                capture_client(hwnd,out/(label+'-after.png'))
                checks[label+'_reached_pride']=after.get('level')==0 and after.get('descriptor')==0xc00387
                key(0x70);slot=out/'tlk_slot1.state';checks[label+'_save_exists']=slot.exists()
                if slot.exists():
                    raw=slot.read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
                    checks[label+'_independent_owners_clear']=raw[at+180:at+192]==bytes(12) and struct.unpack_from('<I',raw,at+100)[0]==0
            boot=out/'tlk_practice_boot.state'
            checks['genuine_boot_checkpoint']=boot.exists() and struct.unpack_from('<I',boot.read_bytes(),12)[0]==0
            checks['final_choice_preserved']='gameplay.levels.pride_lands.final_life = md' in profile.read_text()
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    paths=[Path(__file__),reference,base/'build-report.json',seed]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
