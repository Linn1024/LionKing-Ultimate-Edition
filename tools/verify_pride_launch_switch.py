"""Use the real resource tree to switch native→MD revival→native with boot restarts."""
import json
import os
from pathlib import Path
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import read_rows
from verify_pride_soft_tree import latest
from verify_pride_source_controls import macro_tape
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-launch2';build_path=base/'build-report.json';build=bound(build_path)
    out=base/'switch';out.mkdir();live=out/'live';live.mkdir();profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=live/'host.ini';config.write_text('opengl = 0\nscale = 2\n');tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';raw=out/'level-select.raw';raw.write_bytes(macro_tape(tape.read_bytes()))
    exe=base/'player.exe';assert digest(exe)==build['binary_sha256'];node='gameplay.levels.pride_lands.health_death';trace=live/'presents.jsonl';commands={};checks={};snapshots={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};env=dict(clean,TLK_PRIDE_DIAGNOSTICS=str(live),TLK_SOFT_TREE_LOG=str(trace))
    common=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--no-audio','--no-record']
    cmd=common+['--config',config,'--resource-profile',profile,'--input',tape,'--practice-level',0,'--frames',3000,'--speedrun','practice',
                '--hash-at',','.join(map(str,range(1,3001))),'--wav',live/'audio.wav','--wav-seconds',200,'--dump-window',live/'window.png','--dump-png',live/'guest.png']
    commands['live']=list(map(str,cmd));deadline=time.monotonic()+240
    with (live/'run.log').open('wb') as log:
        proc=subprocess.Popen(commands['live'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);hwnd=None
        def wait(predicate):
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(trace)
                if row and predicate(row):return row
                time.sleep(.005)
            raise AssertionError(('UI timeout',proc.poll(),latest(trace)))
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra);assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra);time.sleep(.055)
        def choose(value,label):
            key(0x7b);wait(lambda r:r['about']==2);key(0x24)
            for _ in range(160):
                row=latest(trace);id=row['choices'][row['selected']][0]
                if id==node:break
                if id=='game' or node.startswith(id+'.'):key(0x27)
                key(0x28)
            assert id==node
            for _ in range(3):
                row=latest(trace)
                if row['choices'][row['selected']][1]==value:break
                key(0x0d)
            row=latest(trace);assert row['choices'][row['selected']][1]==value
            snapshots[label]=row;capture_client(hwnd,live/(label+'.png'));key(0x71)
            wait(lambda r:not r['menu'] and r['field']<1000)
        try:
            while not hwnd and proc.poll() is None and time.monotonic()<deadline:hwnd=window_for(proc.pid);time.sleep(.01)
            assert hwnd;USER32.SetProcessDPIAware();wait(lambda r:r['field']>=1500)
            choose(2,'pending-md');checks['md_choice_persisted']=node+' = md' in profile.read_text()
            def owned(row):
                events=[r for r in read_rows(live/'owner-events.csv') if r['event']=='begin']
                return bool(events) and row['field']>=int(events[0]['field'])+100
            wait(owned);choose(1,'pending-snes-owned');checks['snes_choice_persisted']=node+' = snes' in profile.read_text()
            proc.wait(timeout=120);checks['exit']=proc.returncode==0
        finally:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    boot=live/'tlk_practice_boot.state';checks['genuine_native_poweron_save']=boot.read_bytes()[:8]==b'TLKSTAT1' and int.from_bytes(boot.read_bytes()[12:16],'little')==0
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)';rows=re.findall(pattern,(live/'run.log').read_text());chunks=[]
    for row in rows:
        if not chunks or int(row[0])<=int(chunks[-1][-1][0]):chunks.append([])
        chunks[-1].append(row)
    assert len(chunks)==3,[(len(c),c[:1]) for c in chunks]
    checks['two_actual_boot_restarts']=[r['loaded_field'] for r in read_rows(live/'live-load.csv')]==['0','0','0']
    references={}
    for label,value,end in (('snes','snes',3000),('md','md',int(chunks[1][-1][0]))):
        folder=out/label;folder.mkdir();cfg=folder/'host.ini';cfg.write_bytes(config.read_bytes());choices=folder/'resources.ini';choices.write_text('schema = 1\ngame = snes\n'+node+' = '+value+'\n')
        cmd=common+['--config',cfg,'--resource-profile',choices,'--input-raw',raw,'--load',boot,'--frames',end,'--no-pace','--speedrun','practice',
                    '--hash-at',','.join(map(str,range(1,end+1))),'--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
        commands[label]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[label],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert not r.returncode;references[label]=re.findall(pattern,(folder/'run.log').read_text())
    checks['initial_native_guest_prefix']=chunks[0]==references['snes'][:len(chunks[0])]
    checks['restarted_md_guest']=chunks[1]==references['md']
    checks['restored_native_all_3000_fields']=chunks[2]==references['snes'] and len(chunks[2])==3000
    journal=read_rows(live/'practice-fields.csv');start=int(journal[0]['wav_frames_before_audio'])*4
    audio=wav_data(live/'audio.wav');md_audio=wav_data(out/'md/audio.wav');native_audio=wav_data(out/'snes/audio.wav')
    checks['complete_md_pcm_segment']=audio[start:start+len(md_audio)]==md_audio
    checks['complete_final_native_pcm']=audio[-len(native_audio):]==native_audio
    checks['final_native_guest_picture']=pixels(live/'guest.png')==pixels(out/'snes/guest.png')
    # Practice counters can differ between a source restart and a CLI-loaded
    # control; final guest pixels and every native field stay unmasked above.
    for file in out.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(file)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
    paths=[Path(__file__),build_path,tape,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/verify_pride_source_controls.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,snapshots=snapshots,native_fields_compared=sum(map(len,chunks)),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
