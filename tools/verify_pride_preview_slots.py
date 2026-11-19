"""Use F1/F5 on the packaged player with no behavior/probe environment settings."""
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
from verify_pride_overlay import mixed_toast
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-launch2';package_path=base/'preview-package-audit.json';package=bound(package_path);exe=ROOT/'dist/development-preview/LionKing.exe'
    assert digest(exe)==package['binary_sha256'];out=base/'preview-slots';out.mkdir();profile=out/'resources.ini';profile.write_bytes((ROOT/'profiles/pride-development-preview.ini').read_bytes())
    cfg=out/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n');tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    common=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--config',cfg,'--resource-profile',profile,
            '--input',tape,'--practice-level',0,'--frames',1700,'--no-audio','--no-record','--hash-at',','.join(map(str,range(1,1701)))]
    for name in ('control','live'):
        folder=out/name;folder.mkdir();trace=folder/'presents.jsonl';env=dict(clean,TLK_SOFT_TREE_LOG=str(trace))
        cmd=common+['--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
        if name=='control':cmd+=['--no-pace']
        commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            if name=='control':r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180);assert not r.returncode
            else:
                proc=subprocess.Popen(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);hwnd=None;deadline=time.monotonic()+90
                def wait(predicate):
                    while proc.poll() is None and time.monotonic()<deadline:
                        row=latest(trace)
                        if row and predicate(row):return row
                        time.sleep(.003)
                    raise AssertionError(('slot timeout',proc.poll(),latest(trace)))
                def key(vk):assert USER32.PostMessageW(hwnd,0x100,vk,1) and USER32.PostMessageW(hwnd,0x101,vk,0xc0000001)
                try:
                    while not hwnd and proc.poll() is None and time.monotonic()<deadline:hwnd=window_for(proc.pid);time.sleep(.01)
                    assert hwnd;wait(lambda r:r['field']>=1600);key(0x70)
                    slot=out/'tlk_slot1.state'
                    while not slot.exists() and proc.poll() is None and time.monotonic()<deadline:time.sleep(.005)
                    record=slot.read_bytes();assert record[:8]==b'PRPRAC01';saved=int.from_bytes(record[20:24],'little');before=digest(slot)
                    wait(lambda r:r['field']>=saved+10);key(0x74)
                    wait(lambda r:r['field']<=saved+2);time.sleep(.1);USER32.SetProcessDPIAware();capture_client(hwnd,folder/'client.png');proc.wait(timeout=90);assert not proc.returncode
                finally:
                    if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    a,b=out/'control',out/'live';pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)';rows=lambda f:re.findall(pattern,(f/'run.log').read_text());actual=rows(b);cold=rows(a)
    rewinds=[i for i in range(1,len(actual)) if int(actual[i][0])<int(actual[i-1][0])];assert len(rewinds)==1,rewinds
    at=rewinds[0];attempt=int(actual[at-1][0]);sample_bytes=lambda field:((field+1)*48000*357366//21477272)*4
    expected_audio=wav_data(a/'audio.wav');checks=dict(genuine_f1_save=1600<=saved<1615,
        actual_f5_rewind=actual[at][0]==str(saved+1),all_guest_fields=actual==[r for r in cold if int(r[0])<=attempt]+[r for r in cold if int(r[0])>saved],
        complete_pcm=wav_data(b/'audio.wav')==expected_audio[:sample_bytes(attempt)]+expected_audio[sample_bytes(saved):],
        whole_guest=pixels(a/'guest.png')==pixels(b/'guest.png'),whole_notification_client=pixels(b/'window.png')==mixed_toast(a/'window.png','Loaded slot 1'),
        slot_preserved=digest(out/'tlk_slot1.state')==before,no_research_artifacts=not list(out.rglob('*.rgb')) and not list(out.rglob('owner-events.csv')))
    paths=[Path(__file__),package_path,profile,cfg,tape,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_overlay.py',ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,saved_field=saved,loaded_at=attempt,native_fields_compared=len(actual),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                experimental_preview=True,default_installed_player_replaced=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
