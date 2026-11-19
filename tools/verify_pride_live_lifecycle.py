"""Exercise real menu pauses and cub-palette changes during owned revival."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import environment,read_rows,toast_image
from probe_pride_preparation_state import frame_records,glyph_records
from verify_windows import USER32,window_for,hashes,pixels
from windows_capture import capture_client
from verify_pride_audio_state import wav_data

BASE=ROOT/'build/pride-live-lifecycle'
UI=ROOT/'build/pride-live-error-ui'
CASES={'pause-native':('native-aot','aot','pause'), 'pause-md':('md-lle','lle','pause'),
       'palette-death':('graphics-aot','aot','palette100'),'palette-fade':('md-lle','lle','palette274')}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=tuple(CASES),default='pause-native');args=p.parse_args()
    refname,mode,action=CASES[args.case];ref=UI/'audio-windows'/refname
    r=json.loads((ref/'report.json').read_text());assert r['result']=='PASS'
    build_path=UI/'build-report.json';build=json.loads(build_path.read_text());binary=UI/'error-ui-sdl.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in r['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    out=BASE/'final'/args.case;out.mkdir(parents=True,exist_ok=True)
    width=256 if refname=='native-aot' else 320;entry=1776 if width==256 else 1777;end=entry+311
    profile=out/'resources.ini'
    source_profile=UI/'audio-windows'/('native-aot' if width==256 else 'md-lle')/'resources.ini'
    profile.write_bytes(source_profile.read_bytes());initial_profile=digest(profile)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    tape=ROOT/'build/pride-actor-handoff/inputs'/('snes-default.tape' if width==256 else 'md-default.tape')
    state=ref/'seed/initial.state';live=out/'live';live.mkdir(exist_ok=True)
    command=[str(binary),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),
        '--resource-profile',str(profile),'--config',str(config),'--input',str(tape),'--load',str(state),'--frames',str(end),
        '--no-audio','--no-record','--dump-window',str(live/'window.png'),'--dump-png',str(live/'guest.png'),
        '--wav',str(live/'audio.wav'),'--wav-seconds','100']
    if mode=='lle':command+=['--lle']
    USER32.SetProcessDPIAware();events=[];hwnd=None
    with (live/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=environment(live),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            until=time.monotonic()+50
            def field():
                data=read_rows(live/'restore-fields.csv')
                try:return int(data[-1]['field']) if data else 0
                except (ValueError,KeyError):return 0
            def wait_for(target):
                while field()<target:
                    assert proc.poll() is None and time.monotonic()<until;time.sleep(.002)
            def key(value):
                assert USER32.PostMessageW(hwnd,0x100,value,1)
                assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001)
            while not hwnd:
                hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.004)
            if action=='pause':
                for age in (64,238,269,274,301):
                    wait_for(entry+age);resource=age==238;key(123 if resource else 27)
                    time.sleep(.065);held=field();first=read_rows(live/'render-fields.csv')
                    capture_client(hwnd,live/f'paused-{age}.png');time.sleep(.18)
                    last=field();second=read_rows(live/'render-fields.csv')
                    released=bool(second and second[-1].get('released')=='1')
                    events.append(dict(requested_age=age,paused_field=held,final_field=last,
                        repeated_owned_presentations=len(second)-len(first),already_released=released,resource_tree=resource))
                    assert held==last and (len(second)>len(first) or released),(age,events[-1])
                    if resource:key(27);time.sleep(.02)
                    key(9);wait_for(held+1)
            else:
                age=int(action.removeprefix('palette'));wait_for(entry+age);key(121)
                while b'graphics.sprites.simba.cub.palette = snes' not in profile.read_bytes():
                    assert proc.poll() is None and time.monotonic()<until;time.sleep(.002)
                events.append(dict(requested_age=age,profile_saved_field=field(),palette='snes'))
            proc.wait(timeout=30)
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    assert proc.returncode==0
    control=out/'control'
    if action=='pause':control=ref/'control'
    else:
        control.mkdir(exist_ok=True)
        cold=[arg for arg in command if arg!='--lle']
        for flag in ('--load',):
            at=cold.index(flag);del cold[at:at+2]
        for flag,name in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):cold[cold.index(flag)+1]=str(control/name)
        cold+=['--no-pace']
        if mode=='lle':cold+=['--lle']
        with (control/'run.log').open('wb') as log:
            run=subprocess.run(cold,cwd=ROOT,env=environment(control),stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert run.returncode==0
    checks=dict(guest=hashes(live/'run.log')==hashes(control/'run.log'),
        native_ppu=pixels(live/'guest.png')==pixels(control/'guest.png'))
    actual_pcm,expected_pcm=wav_data(live/'audio.wav'),wav_data(control/'audio.wav')
    checks['native_pcm']=actual_pcm==expected_pcm if action=='pause' else bool(actual_pcm) and actual_pcm==expected_pcm[-len(actual_pcm):]
    actual=frame_records(live/'render-owned.rgb',width);changes=[]
    if action=='pause':
        expected=frame_records(control/'render-owned.rgb',width);checks['owned_records']=actual==expected
        glyphs=dict(glyph_records(control));checks['glyphs']=all(glyphs[field]==data for field,data in glyph_records(live))
        checks['profile_unchanged']=digest(profile)==initial_profile
        checks['full_client']=pixels(live/'window.png')==pixels(control/'window.png')
        checks['five_pauses']=len(events)==5 and all(e['paused_field']==e['final_field'] and
            (e['repeated_owned_presentations']>0 or e['already_released']) for e in events)
    else:
        changed=[age for age,data in actual.items() if struct.unpack_from('<I',data,20)[0]==0]
        first=min(changed);events[-1]['first_new_palette_age']=first
        old=ROOT/'build/pride-actor-handoff/active'/f'md-default-320-all-{mode}-owned'
        before=frame_records(old/'render-owned.rgb',width);after=frame_records(control/'render-owned.rgb',width)
        checks['owned_before_after']=all(data==(before if age<first else after)[age] for age,data in actual.items())
        checks['change_within_owned_phase']=int(action.removeprefix('palette'))<=first<=int(action.removeprefix('palette'))+3 and first<300
        image=pixels(live/'window.png');clean=pixels(control/'window.png')
        checks['full_client']=image==clean or image==toast_image(control/'window.png',live/'guest.png','Applied and saved')
        changes=[first]
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,ref/'report.json',state,source_profile,tape,ROOT/'tools/verify_pride_live_error_ui.py',
        ROOT/'tools/probe_pride_preparation_state.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py',ROOT/'tools/verify_pride_audio_state.py')}
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',case=args.case,checks=checks,events=events,
        source_sha256=sources,binary_sha256=digest(binary),width=width,mode=mode,action=action,
        owned_pixels=len(actual)*width*224,artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],checks,events,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
