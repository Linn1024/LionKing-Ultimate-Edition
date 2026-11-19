"""Verify real F1/F5 failure, recovery and post-handoff palette-choice UI."""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import USER32,window_for,hashes,pixels
from windows_capture import capture_client
from verify_pride_audio_state import wav_data

BASE=ROOT/'build/pride-live-error-ui'
CASES={'native-aot':('snes',256,'native','aot','damaged'),
       'md-lle':('md',320,'all','lle','damaged'),
       'graphics-aot':('md',320,'all','aot','graphics'),
       'missing-aot':('snes',256,'native','aot','missing'),
       'recovery-lle':('md',320,'all','lle','recovery')}


def read_rows(path):
    try:
        with path.open() as f:return [r for r in csv.DictReader(f) if r and all(v is not None for v in r.values())]
    except (OSError,ValueError):return []


def toast_image(reference,guest,message):
    width,height,base=pixels(reference);gw,gh,native=pixels(guest)
    assert (gw,gh)==(256,224) and height==448 and width in (512,640)
    font=(ROOT/'engine/runner/tlk_font8x8.h').read_text()
    glyphs=[[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',row)] for row in re.findall(r'\{([^{}]+)\}',font)]
    assert len(glyphs)==95 and all(len(g)==8 for g in glyphs)
    lines=[];text=message
    while text and len(lines)<9:
        text=text.lstrip(' ')
        if not text:break
        length=len(text.split('\n',1)[0]);take=min(length,30)
        if length>30:
            split=take
            while split and text[split]!=' ':split-=1
            if split:take=split
        lines.append(text[:take]);text=text[take:]
        if text.startswith('\n'):text=text[1:]
    longest=max(map(len,lines));extra=(width//2-256)//2
    for y in range(4,4+len(lines)*10+6):
        for x in range(4,4+longest*8+8):
            p=native[y*256+x];o=tuple(c*25//255 for c in p)
            if y>=8:
                line,row=(y-8)//10,(y-8)%10
                if line<len(lines) and row<8 and 8<=x<8+len(lines[line])*8:
                    char=lines[line][(x-8)//8]
                    if glyphs[ord(char)-32][row]&(1<<((x-8)%8)):o=(255,255,255)
            if o!=p:
                for dy in (0,1):
                    for dx in (0,1):base[(y*2+dy)*width+(extra+x)*2+dx]=o
    return width,height,base


def environment(folder):
    env=os.environ.copy()
    for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
    for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE','TLK_SCENE_RESTORE_ENABLE',
                'TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
    env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
    return env


def run(command,folder):
    folder.mkdir(exist_ok=True)
    with (folder/'run.log').open('wb') as log:
        r=subprocess.run(list(map(str,command)),cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=180)
    assert r.returncode==0,(folder,r.returncode)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=tuple(CASES),default='native-aot');args=p.parse_args()
    start,width,graphics,mode,kind=CASES[args.case];out=BASE/'audio-windows'/args.case;out.mkdir(parents=True,exist_ok=True)
    build_path=BASE/'build-report.json';build=json.loads(build_path.read_text());binary=BASE/'error-ui-sdl.exe'
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    for file,sha in build['source_sha256'].items():assert digest(ROOT/file)==sha,file
    refname=f'{start}-default-{width}-{graphics}-0-'+('aot-lle' if start=='snes' else 'lle-aot')
    reference=ROOT/'build/pride-handoff-state/windows'/refname;r=json.loads((reference/'report.json').read_text())
    assert r['result']=='PASS'
    for file,sha in r['source_sha256'].items():assert digest(ROOT/file)==sha,file
    entry=1776 if start=='snes' else 1777;end=2087 if start=='snes' else 2088
    source_profile=reference/'resources.ini';tape=Path(r['commands']['baseline'][r['commands']['baseline'].index('--input')+1])
    profile=out/'resources.ini';profile.write_bytes(source_profile.read_bytes())
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    common=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',profile,'--config',config,'--input',tape,'--no-audio','--no-record']
    if mode=='lle':common+=['--lle']
    seed=out/'seed';seed.mkdir(exist_ok=True);state=seed/'initial.state'
    run(common+['--frames',entry,'--no-pace','--save-at',entry,state,'--wav',seed/'audio.wav','--wav-seconds','100'],seed)
    live=out/'live';live.mkdir(exist_ok=True);slot=out/'tlk_slot1.state';assert not slot.exists(),'Use a fresh capture directory'
    command=list(map(str,common+['--load',state,'--frames',end,'--dump-window',live/'window.png',
        '--dump-png',live/'guest.png','--wav',live/'audio.wav','--wav-seconds','100']))
    USER32.SetProcessDPIAware();hwnd=None
    with (live/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=environment(live),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            until=time.monotonic()+45
            def field():
                data=read_rows(live/'restore-fields.csv')
                try:return int(data[-1]['field']) if data else 0
                except (ValueError,KeyError):return 0
            def wait_for(target):
                while field()<target:
                    assert time.monotonic()<until and proc.poll() is None;time.sleep(.003)
            def wait_events(count):
                while len(read_rows(live/'live-load.csv'))<count:
                    assert time.monotonic()<until and proc.poll() is None;time.sleep(.003)
            def key(value):
                assert USER32.PostMessageW(hwnd,0x100,value,1)
                assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001)
            while not hwnd:
                hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.005)
            wait_for(entry+267);key(112)
            while not slot.exists():
                assert time.monotonic()<until and proc.poll() is None;time.sleep(.003)
            original=slot.read_bytes();saved=struct.unpack_from('<I',original,20)[0]
            assert original[:8]==b'PRHSAVE1' and entry+267<=saved<=entry+272,saved
            (out/'saved-valid.state').write_bytes(original)
            if kind in ('damaged','recovery'):
                damaged=bytearray(original);damaged[0]^=1;slot.write_bytes(damaged)
            elif kind=='missing':slot.unlink()
            if kind=='graphics':
                wait_for(entry+304);key(121)
                while b'graphics.sprites.simba.cub.palette = snes' not in profile.read_bytes():
                    assert time.monotonic()<until and proc.poll() is None;time.sleep(.003)
            else:wait_for(saved+5)
            key(116);wait_events(2)
            if kind=='recovery':
                slot.write_bytes(original);wait_for(saved+10);key(116);wait_events(3)
                slot.unlink();wait_for(saved+5);key(116);wait_events(4)
            # Late post-handoff tests can reach their endpoint before an extra
            # PrintWindow call. The required final capture is also made by the
            # real SDL/GL client at its exact endpoint below.
            time.sleep(.01)
            if proc.poll() is None:
                try:capture_client(hwnd,live/'error-live.png')
                except AssertionError:pass
            proc.wait(timeout=25)
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    assert proc.returncode==0
    # A fresh uninterrupted control uses the final source choices. F10 occurs
    # after handoff; earlier artwork choices do not alter guest gameplay/audio.
    control=out/'control'
    if kind=='graphics':
        run(common+['--frames',end,'--no-pace','--dump-window',control/'window.png','--dump-png',control/'guest.png',
            '--wav',control/'audio.wav','--wav-seconds','100'],control)
    else:
        run(common+['--load',state,'--frames',end,'--no-pace','--dump-window',control/'window.png','--dump-png',control/'guest.png',
            '--wav',control/'audio.wav','--wav-seconds','100'],control)
    message='Slot 1: '+('Match the saved graphics choices and retry' if kind=='graphics' else
        'Save could not be read' if kind in ('missing','recovery') else 'Save is incompatible or damaged')
    events=read_rows(live/'live-load.csv');wanted=['1','0','1','0'] if kind=='recovery' else ['1','0']
    checks=dict(actual_load_events=[e['success'] for e in events]==wanted,
        error_text=message in (live/'run.log').read_text(),guest=hashes(live/'run.log')==hashes(control/'run.log'),
        native_guest_image=pixels(live/'guest.png')==pixels(control/'guest.png'),
        full_client=pixels(live/'window.png')==toast_image(control/'window.png',live/'guest.png',message))
    expected=wav_data(control/'audio.wav');actual=wav_data(live/'audio.wav')
    samples=lambda f:f*48000*357366//21477272*4
    if kind=='recovery':
        attempt=int(events[2]['attempt_field']);checks['native_pcm']=actual==expected[:samples(attempt)-samples(entry)]+expected[samples(saved)-samples(entry):]
    elif kind=='graphics':checks['native_pcm']=actual==expected[-len(actual):] and len(actual)>0
    else:checks['native_pcm']=actual==expected and len(actual)>0
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,reference/'report.json',source_profile,tape,ROOT/'tools/verify_windows.py',
        ROOT/'tools/windows_capture.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'engine/runner/tlk_font8x8.h',ROOT/'engine/runner/sdl_main.c')}
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',case=args.case,checks=checks,events=events,save_field=saved,
        message=message,binary_sha256=digest(binary),source_sha256=sources,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        actual_f1_f5_used=True,actual_f10_after_release_used=kind=='graphics',public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
