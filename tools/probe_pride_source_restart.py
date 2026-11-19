"""Operate the F12 music leaf during revival and ordinary play, then real F9."""
import argparse
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import USER32,window_for,hashes
from windows_capture import capture_client


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-root',type=Path,required=True);args=p.parse_args()
    out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True);assert not (out/'live/run.log').exists(),'Fresh directory required'
    base=ROOT/'build/pride-raster-state';build_path=base/'build-report.json';build=bound(build_path)
    author_path=base/'live/md-media/report.json';author=bound(author_path);assert author['result']=='PASS'
    binary=base/'live/runtime/practice-live.exe';dll=binary.parent/'genesis_plus_gx_libretro.dll'
    assert digest(binary)==author['binary_sha256']==build['runs']['sdl']['binary_sha256']
    assert digest(dll)==author['dll_sha256']
    profile=out/'resources.ini';profile.write_bytes((author_path.parent/'resources.ini').read_bytes());(out/'initial.ini').write_bytes(profile.read_bytes())
    folder=out/'live';folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    command=list(map(str,[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',profile,'--config',config,'--input',tape,'--frames',3000,'--speedrun','practice',
        '--no-audio','--no-record','--lle','--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
        '--wav',folder/'audio.wav','--wav-seconds',200,'--hash-at',','.join(map(str,range(1,3001)))]))
    (out/'command.json').write_text(json.dumps(command,indent=2)+'\n')
    (out/'driver-source.py').write_text(Path(__file__).read_text())
    env=environment(folder);env['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv');env['TLK_AUDIO_STEMS']=str(folder/'audio-stems.csv')
    # Bounded normal replays intentionally omit the interactive power-on save.
    # Author that exact field0 artifact through the real level-select startup,
    # then supply it beside this run's config as interactive play would do.
    seed=out/'boot-author';seed.mkdir();seed_config=seed/'host.ini';seed_config.write_bytes(config.read_bytes())
    seed_command=list(command)
    seed_command[seed_command.index('--config')+1]=str(seed_config)
    seed_command[seed_command.index('--frames')+1]='2'
    for flag,name in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):
        seed_command[seed_command.index(flag)+1]=str(seed/name)
    seed_command+=['--practice-level','0','--no-pace']
    (out/'boot-author-command.json').write_text(json.dumps(seed_command,indent=2)+'\n')
    with (seed/'run.log').open('wb') as log:
        result=subprocess.run(seed_command,cwd=ROOT,env=environment(seed),stdout=log,stderr=subprocess.STDOUT,timeout=90)
    assert result.returncode==0
    boot=seed/'tlk_practice_boot.state';assert boot.read_bytes()[:8]==b'PRHBOOT1'
    shutil.copyfile(boot,folder/boot.name)
    USER32.SetProcessDPIAware();hwnd=None;until=time.monotonic()+240;events=[]
    with (folder/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            def wait(predicate):
                while not predicate():
                    assert proc.poll() is None and time.monotonic()<until,('Live process/deadline',proc.pid,proc.poll())
                    time.sleep(.004)
            def key(code):
                assert USER32.PostMessageW(hwnd,0x100,code,1);assert USER32.PostMessageW(hwnd,0x101,code,0xc0000001)
            def click(x,y):
                for msg,buttons in ((0x200,0),(0x201,1),(0x202,0)):
                    assert USER32.PostMessageW(hwnd,msg,buttons,x|(y<<16))
                time.sleep(.2)
            def rows():return read_rows(folder/'practice-fields.csv')
            def loads():return read_rows(folder/'live-load.csv')
            def field():
                data=rows();return int(data[-1]['field']) if data else 0
            def shot(name):assert capture_client(hwnd,folder/(name+'.png'))==(960,672)
            while not hwnd:
                hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.005)
            wait(lambda:field()>=2002)
            restart=folder/'tlk_practice_restart.state';wait(restart.exists)
            (out/'automatic-initial.state').write_bytes(restart.read_bytes())
            for index,source in enumerate(('snes','md')):
                if index:wait(lambda:field()>=1500)
                key(123);time.sleep(.15);held=field();before_rows=len(rows());before_loads=len(loads())
                shot(f'{source}-open')
                if not index:
                    click(154,267);click(154,295);click(174,324)
                shot(f'{source}-tree');click(575,352);shot(f'{source}-popup')
                click(490,405 if source=='snes' else 428);shot(f'{source}-staged')
                assert field()==held,'Resource menu must pause guest'
                click(170,595)
                wait(lambda:len(loads())>before_loads)
                load=loads()[-1];assert load['success']=='1' and load['loaded_field']=='0',load
                assert 'audio.music.pride_lands = '+source in profile.read_text(),profile.read_text()
                (out/(source+'.ini')).write_bytes(profile.read_bytes())
                wait(lambda:len(rows())>before_rows and int(rows()[before_rows]['field'])==1)
                wait(lambda:field()>=1450)
                raw=restart.read_bytes();assert raw[:8]==b'PRPRAC01'
                saved=struct.unpack_from('<I',raw,20)[0];assert saved==1427,saved
                (out/f'automatic-{source}.state').write_bytes(raw)
                events.append(dict(source=source,paused_field=held,row_boundary=before_rows,load=load,automatic_field=saved))
                shot(f'{source}-restarted')
            prior=len(loads());before_rows=len(rows());key(120)
            wait(lambda:len(loads())>prior)
            load=loads()[-1];assert load['success']=='1' and load['loaded_field']=='1427',load
            events.append(dict(action='f9',row_boundary=before_rows,load=load))
            time.sleep(.06);shot('f9-restarted');code=proc.wait(timeout=150)
        finally:
            if proc.poll() is None:
                USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks=dict(exit=code==0,three_loads=len(loads())==3 and all(r['success']=='1' for r in loads()),
        from_owned=2002<=events[0]['paused_field']<=2015,from_ordinary=1500<=events[1]['paused_field']<=1512,
        f9_updated_state=restart.read_bytes()==(out/'automatic-md.state').read_bytes(),
        changed_restart_snapshot=(out/'automatic-snes.state').read_bytes()!=(out/'automatic-md.state').read_bytes(),
        same_level=all(r['level']=='0' for r in rows() if int(r['field'])>=1427))
    paths=(Path(__file__),build_path,author_path,tape,ROOT/'tools/windows_capture.py',ROOT/'tools/verify_pride_live_error_ui.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,events=events,binary_sha256=digest(binary),dll_sha256=digest(dll),
        command=command,guest=hashes(folder/'run.log'),source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        full_first_level_fidelity_complete=False,public_player_enabled=False,exact_audio_and_scene_control_comparison=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,events,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
