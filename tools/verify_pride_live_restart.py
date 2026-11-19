"""Actual repeated F9 from live revival, including selected MD audio."""
import argparse
import json
from pathlib import Path
import shutil
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data, audio_offset
from verify_pride_live_error_ui import environment, read_rows
from verify_windows import USER32, window_for, hashes, pixels
from windows_capture import capture_client


def prefix_equal(part, whole):
    if not part.exists(): return True
    if not whole.exists(): return False
    with part.open('rb') as a, whole.open('rb') as b:
        while chunk := a.read(1024*1024):
            if chunk != b.read(len(chunk)): return False
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', choices=('native','md-graphics','md-music','md-media'), required=True)
    args=p.parse_args(); md=args.case!='native'; audio=args.case in ('md-music','md-media')
    base=ROOT/'build/pride-practice-live'; base.mkdir(exist_ok=True)
    out=base/args.case; out.mkdir(exist_ok=True)
    assert not (out/'report.json').exists(), 'Use a fresh completed capture directory'
    build_path=ROOT/'build/pride-overlay/build-report.json'; build=bound(build_path)
    source=ROOT/'build/pride-overlay/overlay-sdl.exe'; dll=ROOT/'dist/genesis_plus_gx_libretro.dll'
    assert digest(source)==build['runs']['sdl']['binary_sha256']
    runtime=base/'runtime'; runtime.mkdir(exist_ok=True)
    for original, name in ((source,'practice-live.exe'),(dll,dll.name)):
        target=runtime/name
        if target.exists(): assert digest(target)==digest(original),target
        else: shutil.copyfile(original,target)
    binary=runtime/'practice-live.exe'
    old=ROOT/'build/pride-overlay/windows'/('md-owned' if md else 'native-owned')/'resources.ini'
    profile=out/'resources.ini'
    profile.write_text(old.read_text()+('audio.music.pride_lands = md\n' if audio else '')+('audio.effects = md\n' if args.case=='md-media' else ''))
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'; commands={}
    def command(name):
        folder=out/name; folder.mkdir(exist_ok=True)
        config=folder/'host.ini'; config.write_text('opengl = 1\nscale = 2\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input',tape,'--frames',3000,
             '--speedrun','practice','--no-audio','--no-record','--dump-window',folder/'window.png',
             '--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',200]
        if md: cmd+=['--lle']
        return folder,list(map(str,cmd))
    def env(folder):
        e=environment(folder); e['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv')
        e['TLK_AUDIO_STEMS']=str(folder/'audio-stems.csv'); return e
    baseline,cmd=command('baseline'); cmd+=['--no-pace']; commands['baseline']=cmd
    with (baseline/'run.log').open('wb') as log:
        r=subprocess.run(cmd,cwd=ROOT,env=env(baseline),stdout=log,stderr=subprocess.STDOUT,timeout=240)
    assert r.returncode==0,('baseline',r.returncode)
    begins=[int(r['field']) for r in read_rows(baseline/'owner-events.csv') if r['event']=='begin']
    assert len(begins)==2, begins
    restart=baseline/'tlk_practice_restart.state'; original=restart.read_bytes()
    assert original[:8]==b'PRPRAC01'; saved=struct.unpack_from('<I',original,20)[0]
    # A real selected-MD continuation envelope must be present, not merely a
    # requested profile leaf silently falling back to native playback.
    native_size=struct.unpack_from('<I',original,16)[0]
    native=original[256:256+native_size]; at=audio_offset(native)
    assert native[at:at+8]==b'TLKAUD01'
    nested=struct.unpack_from('<I',native,at+40)[0]
    live,cmd=command('live'); commands['live']=cmd
    USER32.SetProcessDPIAware(); hwnd=None; until=time.monotonic()+210
    observed=[]
    with (live/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env(live),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while not hwnd:
                hwnd=window_for(proc.pid); assert proc.poll() is None and time.monotonic()<until; time.sleep(.005)
            for index,age in enumerate((225,270)):
                target=begins[0]+age
                while True:
                    rows=read_rows(live/'practice-fields.csv')
                    if rows and int(rows[-1]['field'])>=target: break
                    assert proc.poll() is None and time.monotonic()<until; time.sleep(.003)
                assert USER32.PostMessageW(hwnd,0x100,120,1)
                assert USER32.PostMessageW(hwnd,0x101,120,0xc0000001)
                while len(read_rows(live/'live-load.csv'))<index+1:
                    assert proc.poll() is None and time.monotonic()<until; time.sleep(.003)
                load=read_rows(live/'live-load.csv')[-1]; observed.append(load)
                assert load['success']=='1' and int(load['loaded_field'])==saved,load
                # A real Win32 client capture supplements the exact endpoint
                # dumps. It is illustrative; its field is not assumed exact.
                time.sleep(.04); capture_client(hwnd,live/f'restart-{index+1}-toast.png')
            code=proc.wait(timeout=150)
        finally:
            if proc.poll() is None:
                USER32.PostMessageW(hwnd,0x10,0,0)
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: proc.terminate(); proc.wait(timeout=5)
    attempts=[int(r['attempt_field']) for r in observed]
    checks=dict(exit=code==0,two_f9=len(observed)==2,
        first_owned=begins[0]+225<=attempts[0]<=begins[0]+230,
        second_owned=begins[0]+270<=attempts[1]<=begins[0]+273,
        automatic_equal=original==(live/'tlk_practice_restart.state').read_bytes(),
        guest=hashes(live/'run.log')==hashes(baseline/'run.log'),
        native_image=pixels(live/'guest.png')==pixels(baseline/'guest.png'),
        md_library_ready='MD audio ready' in (live/'run.log').read_text(),
        audio_payload=(nested>0)==audio)
    controls=read_rows(baseline/'practice-fields.csv'); rows=read_rows(live/'practice-fields.csv')
    rewinds=[i for i in range(1,len(rows)) if int(rows[i]['field'])<int(rows[i-1]['field'])]
    checks['two_rewinds']=len(rewinds)==2
    assert len(rewinds)==2,rewinds
    first,second=[int(rows[i]['wav_frames_before_audio'])*4 for i in rewinds]
    def cut(field):
        matches=[r for r in controls if int(r['field'])==field+1]; assert len(matches)==1
        return int(matches[0]['wav_frames_before_audio'])*4
    pcm=wav_data(live/'audio.wav'); ref=wav_data(baseline/'audio.wav'); start=cut(saved)
    checks['initial_pcm']=pcm[:first]==ref[:cut(attempts[0])]
    checks['first_replay_pcm']=pcm[first:second]==ref[start:cut(attempts[1])]
    checks['second_replay_pcm']=pcm[second:]==ref[start:]
    def project(items):
        return ([r for r in items if int(r['field'])<=attempts[0]]+
                [r for r in items if saved<int(r['field'])<=attempts[1]]+
                [r for r in items if int(r['field'])>saved])
    wanted=project(controls)
    checks['every_field_guest_context']=[[r[k] for k in ('field','level','state','health')] for r in rows]==[[r[k] for k in ('field','level','state','health')] for r in wanted]
    checks['every_frontend_clock']=all(int(r['frontend_before_increment'])==int(r['field'])-1 for r in rows)
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv','bank-clock.csv'):
        checks[name]=read_rows(live/name)==project(read_rows(baseline/name))
    for folder,prior,label,complete in ((live,baseline,'first-prefix',False),(live/'restart-1',baseline,'second-prefix',False),
        (live/'restart-2',baseline,'replayed-first',True),(live/f'restart-2/scene-{begins[1]}',baseline/f'scene-{begins[1]}','replayed-second',True)):
        for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv'):
            checks[label+'/'+name]=digest(folder/name)==digest(prior/name) if complete else prefix_equal(folder/name,prior/name)
        if complete:
            for name in ('ground-entry.bin','ground-return.bin'): checks[label+'/'+name]=digest(folder/name)==digest(prior/name)
    # F9 deliberately marks the whole-run timer dirty and keeps its elapsed
    # time. Compare all other client pixels, including the level timer, rather
    # than pretending that this intentional value must equal uninterrupted play.
    width,height,a=pixels(baseline/'window.png'); w,h,b=pixels(live/'window.png'); assert (w,h)==(width,height)
    extra=(width//2-256)//2
    ignored={(y*2+dy)*width+(extra+x)*2+dx for y in range(13,21) for x in range(68,156) for dy in (0,1) for dx in (0,1)}
    checks['client_except_elapsed_run_value']=all(x==y for i,(x,y) in enumerate(zip(a,b)) if i not in ignored)
    paths=(Path(__file__),build_path,source,dll,profile,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/windows_capture.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,
        observed_loads=observed,saved_field=saved,revival_begins=begins,pcm_cuts=[first,second],
        md_audio_selected=audio,md_audio_payload_bytes=nested,compared_client_pixels=len(a)-len(ignored),
        binary_sha256=digest(binary),dll_sha256=digest(dll),source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},commands=commands,
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        public_player_enabled=False,mixed_ui_overlay_fidelity_complete=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(args.case,report['result'],[k for k,v in checks.items() if not v],observed,flush=True)
    if not all(checks.values()): raise SystemExit(1)


if __name__=='__main__': main()
