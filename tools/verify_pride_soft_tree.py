"""Exercise the fallback resource tree through real Windows messages."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment
from verify_pride_audio_state import wav_data
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client

PRESET='schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.sprites.simba.cub.palette = md\ngraphics.sprites.simba.adult.palette = md\n'


def latest(path):
    try:
        with path.open('rb') as f:
            f.seek(0,2);f.seek(max(0,f.tell()-65536));lines=f.read().splitlines()
        for line in reversed(lines):
            try:return json.loads(line)
            except (ValueError,UnicodeError):pass
    except OSError:pass
    return None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=('native','md'),required=True);args=parser.parse_args()
    base=ROOT/'build/pride-soft-tree';build_path=base/'build-report.json';build=bound(build_path)
    binary=base/'singlepass.exe';assert digest(binary)==build['binary_sha256']
    old_path=ROOT/'build/pride-singlepass/build-report.json';old=bound(old_path)
    out=base/'windows'/args.case;out.mkdir(parents=True)
    initial=PRESET if args.case=='md' else 'schema = 1\ngame = snes\n'
    checks={};commands={};snapshots={}
    for name,exe in (('control',ROOT/'build/pride-singlepass/singlepass.exe'),('candidate',binary)):
        folder=out/name;folder.mkdir();profile=folder/'resources.ini';profile.write_text(initial)
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,
             '--practice-level','0','--frames','1800','--no-pace','--no-audio','--no-record','--dump-png',folder/'guest.png',
             '--wav',folder/'audio.wav','--wav-seconds','100','--hash-at',','.join(map(str,range(1,1801)))]
        if args.case=='md':cmd+=['--lle']
        if name=='candidate':cmd+=['--menu-at','1500','--menu-page','resources']
        else:cmd+=['--dump-window',folder/'window.png']
        commands[name]=list(map(str,cmd));env=environment(folder);trace=folder/'tree.jsonl';env['TLK_SOFT_TREE_LOG']=str(trace)
        with (folder/'run.log').open('wb') as log:
            if name=='control':
                r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180);assert not r.returncode
                continue
            proc=subprocess.Popen(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            hwnd=None
            def wait(predicate,seconds=15):
                deadline=time.monotonic()+seconds
                while proc.poll() is None and time.monotonic()<deadline:
                    row=latest(trace)
                    if row and predicate(row):return row
                    time.sleep(.01)
                raise AssertionError(('UI state timeout',proc.poll(),latest(trace)))
            def key(vk):
                scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if vk in (0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28) else 0
                assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
                assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra)
                time.sleep(.055)
                return latest(trace)
            def choice(row,id):return next(c for c in row['choices'] if c[0]==id)
            def select(id):
                key(0x24)
                for _ in range(150):
                    row=latest(trace);selected=row['choices'][row['selected']][0]
                    if selected==id:return row
                    if id.startswith(selected+'.') or selected=='game':key(0x27)
                    key(0x28)
                raise AssertionError(('node not reachable',id,latest(trace)))
            def setchoice(id,value):
                select(id)
                for _ in range(3):
                    row=latest(trace)
                    if choice(row,id)[1]==value:return row
                    key(0x0d)
                return wait(lambda r:choice(r,id)[1]==value)
            def snap(name):
                row=latest(trace);snapshots[name]=row;capture_client(hwnd,folder/(name+'.png'));return row
            def apply():
                key(0x71);wait(lambda r:r['modal']==1);key(0x1b)
            try:
                wait(lambda r:r['menu']==1 and r['about']==2,120);hwnd=window_for(proc.pid);assert hwnd
                USER32.SetProcessDPIAware();row=snap('initial');checks['plain_editor']=row['gl']==0 and row['field']==1500
                baseline=profile.read_bytes()
                setchoice('graphics.sprites.simba.cub',2);row=setchoice('graphics.sprites.simba.cub.palette',1)
                checks['branch_inheritance']=choice(row,'graphics.sprites.simba.cub.frames')[3]==2 and choice(row,'graphics.sprites.simba.cub.palette')[3]==1
                checks['draft_not_published']=profile.read_bytes()==baseline and row['dirty']==1
                apply();row=snap('inherited');checks['live_apply']=row['field']==1500 and row['dirty']==0 and choice(row,'graphics.sprites.simba.cub.frames')[4]==2
                checks['profile_persisted']='graphics.sprites.simba.cub = md' in profile.read_text() and 'graphics.sprites.simba.cub.palette = snes' in profile.read_text()
                saved=profile.read_bytes();setchoice('graphics.sprites.simba.cub.palette',2);key(0x72)
                row=latest(trace);checks['revert']=row['dirty']==0 and profile.read_bytes()==saved and choice(row,'graphics.sprites.simba.cub.palette')[1]==1
                setchoice('graphics.sprites.simba.adult.frames',2);key(0x71);row=snap('blocked')
                checks['unsupported_apply_blocked']=row['modal']==1 and row['dirty']==1 and profile.read_bytes()==saved and choice(row,'graphics.sprites.simba.adult.frames')[2]!=2
                key(0x1b);key(0x72)
                select('graphics.sprites.simba.cub.palette');key(0x48);row=snap('scope');checks['scope_help']=row['modal']==1;key(0x1b)
                # F6 stages the documented graphics mix; Apply uses the shared host resize.
                key(0x75);checks['preset_is_draft']=profile.read_bytes()==saved;apply();row=snap('mixed-width')
                checks['md_width']=row['width']==320 and pixels(folder/'mixed-width.png')[:2]==(640,448)
                # At 320 pixels, mouse mapping must still target the centred 256-pixel menu.
                key(0x24);key(0x28);key(0x28);row=latest(trace);assert row['choices'][row['selected']][0]=='display.viewport'
                x,y=(32+220)*2,(52+2*11+3)*2
                assert USER32.PostMessageW(hwnd,0x201,1,x+(y<<16));assert USER32.PostMessageW(hwnd,0x202,0,x+(y<<16));time.sleep(.1)
                row=latest(trace);checks['mouse_after_resize']=choice(row,'display.viewport')[1]==0 and row['dirty']==1
                key(0x72);key(0x73);apply();row=snap('snes-width')
                checks['snes_width']=row['width'] in (0,256) and pixels(folder/'snes-width.png')[:2]==(512,448)
                if args.case=='md':key(0x75);apply()
                row=latest(trace);checks['paused_through_edits']=row['field']==1500
                # A cancelled nested edit must not change persistence; closing/reopening retains applied values.
                saved=profile.read_bytes();setchoice('graphics.sprites.simba.cub.frames',2);key(0x1b)
                checks['cancel']=profile.read_bytes()==saved and latest(trace)['about']==0
                key(0x1b)  # leave Resources section
                key(0x1b)  # close settings
                # Process can finish immediately in no-pace mode; all final checks use guest logs.
                proc.wait(timeout=180);assert not proc.returncode,proc.returncode
            finally:
                if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        print(args.case,name,'exit0',flush=True)
    a,b=out/'control',out/'candidate';pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda f:re.findall(pattern,(f/'run.log').read_text())
    checks['all_guest_fields']=rows(a)==rows(b) and len(rows(b))>=1800
    checks['final_guest_picture']=pixels(a/'guest.png')==pixels(b/'guest.png')
    checks['complete_pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
    trace_rows=[json.loads(line) for line in (b/'tree.jsonl').read_text().splitlines()]
    checks['one_overlay_pass']=bool(trace_rows) and all(r['passes']==1 for r in trace_rows)
    paths=[Path(__file__),build_path,old_path,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py',ROOT/'tools/verify_pride_audio_state.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,snapshots=snapshots,presentations=len(trace_rows),
                binary_sha256=build['binary_sha256'],prior_binary_sha256=old['binary_sha256'],source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
