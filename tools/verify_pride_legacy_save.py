"""Verify genuine legacy-save rejection and current-save continuation in Windows."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_pride_overlay import mixed_toast
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','mixed-native','mixed-md'),required=True);args=p.parse_args()
    root=ROOT/'build/pride-legacy-save';build_path=root/'player/build-report.json';build=bound(build_path)
    prior_path=root/'probe/report.json';prior=bound(prior_path);md=args.case=='mixed-md';private=args.case!='native'
    host='mixed' if private else 'native';binary=root/'player'/(host+'.exe');assert digest(binary)==build['runs'][host]['binary_sha256']
    out=root/'verified'/args.case;out.mkdir(parents=True);source=root/'probe'/('md-media' if md else 'native');legacy=source/'installed.state'
    profile=out/'resources.ini';profile.write_bytes((source/'resources.ini').read_bytes());tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    config=out/'host.ini';config.write_text(f'opengl = {int(args.case=="mixed-native")}\nscale = 2\n')
    slot=out/'tlk_slot1.state';shutil.copy2(legacy,slot);original=digest(slot)
    common=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,
            '--input',tape,'--no-audio','--no-record']
    if md:common+=['--lle']
    commands={};checks={};entry=2001;end=2061;state=out/'current.state'
    def env(folder):
        value=environment(folder);value['TLK_SOFT_TREE_LOG']=str(folder/'presents.jsonl');value['TLK_AUDIO_STEMS']=str(folder/'stems.csv');return value
    def run(name,cmd):
        folder=out/name;folder.mkdir();commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[name],cwd=ROOT,env=env(folder),stdout=log,stderr=subprocess.STDOUT,timeout=180)
        return folder,r.returncode
    cli,code=run('legacy-cli',common+['--load',slot,'--frames',1510,'--no-pace'])
    message=('Native save format: use its original player or restart level' if private else 'State runtime is incompatible or damaged; use its original player')
    checks['legacy_cli_rejected']=code==8;checks['accurate_cli_diagnosis']=message in (cli/'run.log').read_text() and 'audio continuation' not in (cli/'run.log').read_text()
    author,code=run('author',common+['--frames',entry,'--save-at',entry,state,'--no-pace']);assert not code and state.exists()
    if private:checks['genuine_owned_save']=state.read_bytes()[:8]==b'PRHSAVE1'
    else:checks['current_native_save']=state.read_bytes()[:8]==b'TLKSTAT1'
    control,code=run('control',common+['--load',state,'--frames',end,'--no-pace','--dump-window',out/'control/window.png','--dump-png',out/'control/guest.png',
                                          '--wav',out/'control/audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(entry+1,end+1)))]);assert not code
    live=out/'live';live.mkdir();trace=live/'presents.jsonl'
    cmd=common+['--load',state,'--frames',end,'--dump-window',live/'window.png','--dump-png',live/'guest.png','--wav',live/'audio.wav','--wav-seconds',100,
                '--hash-at',','.join(map(str,range(entry+1,end+1)))];commands['live']=list(map(str,cmd))
    with (live/'run.log').open('wb') as log:
        proc=subprocess.Popen(commands['live'],cwd=ROOT,env=env(live),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);hwnd=None;deadline=time.monotonic()+60
        try:
            while proc.poll() is None and time.monotonic()<deadline:
                if not hwnd:hwnd=window_for(proc.pid)
                row=latest(trace)
                if hwnd and row and row['field']>=entry+10:break
                time.sleep(.003)
            assert hwnd and proc.poll() is None and row['field']<entry+20,('no live F5 target',row)
            attempted=row['field'];USER32.SetProcessDPIAware()
            assert USER32.PostMessageW(hwnd,0x100,0x74,1);assert USER32.PostMessageW(hwnd,0x101,0x74,0xc0000001)
            time.sleep(.10);capture_client(hwnd,live/'client.png');proc.wait(timeout=60);assert not proc.returncode,proc.returncode
        finally:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)';rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    checks['all_video_full_wram_fields']=rows(control)==rows(live) and len(rows(live))==60
    checks['complete_recorded_pcm']=wav_data(control/'audio.wav')==wav_data(live/'audio.wav') and bool(wav_data(live/'audio.wav'))
    checks['final_guest_picture']=pixels(control/'guest.png')==pixels(live/'guest.png')
    toast='Slot 1: '+message;checks['accurate_live_f5_diagnosis']=toast in (live/'run.log').read_text()
    checks['independent_whole_client_toast']=pixels(live/'window.png')==mixed_toast(control/'window.png',toast)
    checks['legacy_file_preserved']=digest(slot)==original==digest(legacy)
    checks['all_md_stems']=read_rows(control/'stems.csv')==read_rows(live/'stems.csv')
    presents=[json.loads(line) for line in trace.read_text().splitlines()];checks['one_overlay_pass']=bool(presents) and all(r['passes']==1 for r in presents)
    if private:
        events=read_rows(live/'live-load.csv');checks['exactly_one_failed_actual_f5']=[r['success'] for r in events]==['1','0'] and int(events[-1]['attempt_field'])>=attempted
        for filename in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','scenery-evidence.json'):
            checks[filename]=(control/filename).exists()==(live/filename).exists() and (not (control/filename).exists() or digest(control/filename)==digest(live/filename))
    for rgb in out.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(rgb)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
    paths=[Path(__file__),build_path,prior_path,legacy,tape,ROOT/'tools/verify_pride_overlay.py',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py',ROOT/'engine/runner/tlk_font8x8.h']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,message=message,actual_f5_field=attempted,native_fields_compared=60,
                binary_sha256=build['runs'][host]['binary_sha256'],source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False,legacy_migration_verified=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
