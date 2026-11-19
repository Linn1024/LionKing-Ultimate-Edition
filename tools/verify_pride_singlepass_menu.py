"""Compare actual paused menus against the preceding corrected mixed frontend."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md'),required=True);p.add_argument('--software',action='store_true');p.add_argument('--reuse-completed',action='store_true');args=p.parse_args()
    base=ROOT/'build/pride-singlepass';build_path=base/'build-report.json';build=bound(build_path)
    old=ROOT/'build/pride-machine-player4';old_path=old/'build-report.json';prior=bound(old_path)
    out=base/'menus'/(args.case+('-sdl' if args.software else '-gl'));out.mkdir(parents=True,exist_ok=args.reuse_completed)
    assert not (out/'report.json').exists(),'Preserve completed evidence'
    md=args.case=='md';end=2002 if md else 2001
    author=ROOT/'build/pride-source-live/seeded/resources.ini';profile=out/'resources.ini';profile.write_bytes(author.read_bytes() if md else b'schema = 1\ngame = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={};checks={}
    for name,binary,identity in (('before',old/'machine.exe',prior['binary_sha256']),('after',base/'singlepass.exe',build['binary_sha256'])):
        assert digest(binary)==identity
        folder=out/name;folder.mkdir(exist_ok=args.reuse_completed);config=folder/'host.ini';config.write_text(f'opengl = {int(not args.software)}\nscale = 2\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,'--input',tape,'--frames',end+1,'--speedrun','practice','--menu-at',end,'--menu-page','resources','--no-audio','--no-record','--no-pace','--dump-window',folder/'window.png','--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,end+1)))]
        if md:cmd+=['--lle']
        commands[name]=list(map(str,cmd));env=environment(folder);env['TLK_SINGLEPASS_LOG']=str(folder/'presents.csv')
        if args.reuse_completed:
            text=(folder/'run.log').read_text()
            assert 'dump_window=' in text and 'frame_sha256=' in text and 'wav=' in text,(name,'incomplete preserved run')
        else:
            with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
            assert not r.returncode,(name,r.returncode)
        for path in folder.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
        print(out.name,name,'exit0',flush=True)
    a,b=out/'before',out/'after';pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda f:re.findall(pattern,(f/'run.log').read_text())
    checks['every_native_field']=rows(a)==rows(b) and len(rows(b))==end
    checks['whole_menu_client']=pixels(a/'window.png')==pixels(b/'window.png')
    checks['complete_pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
    presents=read_rows(b/'presents.csv');checks['menu_presented']=any(r['menu']=='1' for r in presents)
    checks['one_overlay_pass']=bool(presents) and all(r['toast_calls']=='1' for r in presents)
    checks['practice_enabled']=all(r['practice']=='1' for r in presents)
    for filename in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','scenery-evidence.json'):
        checks[filename]=(a/filename).exists()==(b/filename).exists() and (not (a/filename).exists() or digest(a/filename)==digest(b/filename))
    paths=[Path(__file__),build_path,old_path,author,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,binary_sha256=build['binary_sha256'],prior_binary_sha256=prior['binary_sha256'],
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out.name,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
