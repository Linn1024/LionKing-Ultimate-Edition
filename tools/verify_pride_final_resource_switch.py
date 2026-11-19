"""Use the actual F12 tree to leave an owned final scene and enable it again."""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-final-resource2';build=base/'build-report.json';bound(build)
    reference=base/'lifecycle/report.json';previous=bound(reference)
    out=base/'switch2';out.mkdir();profile=out/'resources.ini'
    profile.write_bytes((base/'lifecycle/resources.ini').read_bytes())
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    trace=out/'tree.jsonl';node='gameplay.levels.pride_lands.final_life'
    seed=base/'lifecycle/ordinary-start-menu/saved.state'
    cmd=previous['commands']['cold-menu'].copy()
    cmd[cmd.index('--config')+1]=str(config);cmd[cmd.index('--resource-profile')+1]=str(profile)
    cmd[cmd.index('--load')+1]=str(seed);cmd[cmd.index('--frames')+1]='5300';cmd.remove('--no-pace')
    for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/name)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};env['TLK_SOFT_TREE_LOG']=str(trace)
    # Scripted CLI loads intentionally skip the frontend's interactive boot
    # checkpoint. Produce it through an ordinary practice boot first, as normal
    # interactive play does; never fabricate a reset state from the late save.
    prepare=[str(base/'player.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
        '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
        '--resource-profile',str(profile),'--practice-level','0','--frames','1',
        '--no-pace','--no-audio','--no-record']
    with (out/'prepare.log').open('wb') as log:
        subprocess.run(prepare,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    checks={};snapshots={};deadline=time.monotonic()+180;hwnd=None
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait(predicate):
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(trace)
                if row and predicate(row):return row
                time.sleep(.005)
            raise AssertionError(('UI timeout',proc.poll(),latest(trace)))
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
            assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
        def choose(value,label):
            key(0x7b);wait(lambda r:r['about']==2);key(0x24)
            for _ in range(180):
                row=latest(trace);selected=row['choices'][row['selected']][0]
                if selected==node:break
                if selected=='game' or node.startswith(selected+'.'):key(0x27)
                key(0x28)
            assert selected==node
            for _ in range(3):
                if latest(trace)['choices'][row['selected']][1]==value:break
                key(0x0d)
            snapshots[label]=latest(trace);capture_client(hwnd,out/(label+'.png'))
            key(0x71);wait(lambda r:not r['menu'] and r['field']<1000)
            checks[label+'_persisted']=node+' = '+('md' if value==2 else 'snes') in profile.read_text()
        try:
            USER32.SetProcessDPIAware()
            while not hwnd:
                hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<deadline;time.sleep(.005)
            wait(lambda r:r['field']>=3800)
            choose(1,'native-from-final')
            wait(lambda r:r['field']>=1000);key(0x70)
            checks['native_save_exists']=(out/'tlk_slot1.state').exists()
            choose(2,'md-from-native')
            wait(lambda r:r['field']>=1000);key(0x71)
            saved=(out/'tlk_slot2.state').read_bytes()
            checks['reenabled_outer_v3']=saved[:8]==b'TLKFSV01' and struct.unpack_from('<I',saved,8)[0]==3
            fixed=96+struct.unpack_from('<I',saved,20)[0]
            checks['restarted_episode_is_clear']=struct.unpack_from('<I',saved,fixed+100)[0]==0
            checks['real_poweron_restart']=struct.unpack_from('<I',(out/'tlk_practice_boot.state').read_bytes(),12)[0]==0
            # Load a genuine matching final checkpoint through the normal slot UI.
            shutil.copyfile(seed,out/'tlk_slot3.state');key(0x76)
            wait(lambda r:r['field']>=3800);key(0x73)
            capture_client(hwnd,out/'reenabled-final.png')
            saved=(out/'tlk_slot4.state').read_bytes();fixed=96+struct.unpack_from('<I',saved,20)[0]
            checks['reenabled_final_entry']=struct.unpack_from('<I',saved,fixed+100)[0]==3793
            checks['reenabled_final_origin']=bool(struct.unpack_from('<I',saved,fixed+108)[0]&4)
            checks['nonfinal_choice_preserved']='gameplay.levels.pride_lands.health_death = md' in profile.read_text()
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    paths=[Path(__file__),build,reference,seed]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,prepare_command=prepare,snapshots=snapshots,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
