"""Exercise research bulk slices while retaining real CPU/SPC packet completion."""
import csv
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    base=ROOT/'build/pride-title-upload-prototype5';control=base/'report.json';data=bound(control)
    original=ROOT/'build/pride-title-audio-protocol/report.json';bound(original)
    package=ROOT/'build/pride-title-bank-installed/setup-verification/Game data & title bank/install.json'
    info=json.loads(package.read_text());bank=package.parent/info['title_bank_assets']['file']
    out=ROOT/'build/pride-title-upload-fast5';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for width in (256,320):
        folder=out/str(width);folder.mkdir();cmd=data['commands'][str(width)].copy()
        for flag,value in [('--config',out/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        actual=dict(env,TLK_FINAL_MD_ART='1',TLK_TITLE_AUDIO_DIR=str(folder),TLK_TITLE_UPLOAD_FAST='1',TLK_TITLE_UPLOAD_BANK=str(bank),TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[str(width)]=cmd;checks[f'{width}_exit']=r.returncode==0
        print(width,'exit',r.returncode,flush=True)
        if r.returncode:continue
        before=(folder/'before-aram.bin').read_bytes();after=(folder/'after-aram.bin').read_bytes()
        prior=(base/str(width)/'after-aram.bin').read_bytes();wram=(folder/'after-wram.bin').read_bytes();old=(base/str(width)/'after-wram.bin').read_bytes()
        rows=list(csv.reader((folder/'upload.csv').open()));copies=[r for r in rows if r and r[0]=='copy']
        checks[f'{width}_all_sixteen_packets']=len(copies)==16 and {int(r[2]) for r in copies}==set(range(16))
        checks[f'{width}_even_loop_phase']=all(int(r[4])%4==0 for r in copies)
        checks[f'{width}_owned_aram_matches_original']=after[0x25c8:0xf4fb]==prior[0x25c8:0xf4fb]
        checks[f'{width}_directory_matches_original']=after[0x2300:0x25c8]==prior[0x2300:0x25c8]
        checks[f'{width}_host_driver_matches_original']=wram[0x1f00:0x2000]==old[0x1f00:0x2000]
        events=[json.loads(line) for line in (folder/'audio.jsonl').read_text().splitlines()]
        checks[f'{width}_quiet_return']=not any(events[1]['gains']) and not any(events[1]['keys_on']) and not events[1]['queue_depth']
        frames=list(csv.reader((folder/'exit.csv').open()));first=next(int(r[1]) for r in frames if r[0]=='frame' and r[2]=='c005ab' and int(r[5]))
        observations[str(width)]=dict(events=events,first_title=first,remaining_fields=first-370,
            outside_payload_aram_differences=[hex(i) for i in range(0x25c8) if after[i]!=prior[i]],
            host_driver_differences=[hex(i) for i in range(0x1f00,0x2000) if wram[i]!=old[i]])
        print(width,'first title',first,'audio fields',events[1]['age']-events[0]['age'],'host delta',observations[str(width)]['host_driver_differences'],flush=True)
    paths=[Path(__file__),control,original,package,bank,ROOT/'tools/pride_title_upload_slice.inc']
    report=dict(result='OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                scope='Research LLE bulk slice only; not a shipped runtime adapter or full audio fidelity claim',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)

if __name__=='__main__':main()
