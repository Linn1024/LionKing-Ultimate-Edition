"""Compare original and research fast transfer for ordinary Continue NO/timeout."""
import csv
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm

def main():
    source=ROOT/'build/pride-title-native15/contexts/report.json';data=bound(source)
    prototype=ROOT/'build/pride-title-upload-prototype5/report.json';bound(prototype)
    manifest=ROOT/'build/pride-title-bank-installed/setup-verification/Game data & title bank/install.json';info=json.loads(manifest.read_text());bank=manifest.parent/info['title_bank_assets']['file']
    out=ROOT/'build/pride-title-upload-contexts5';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(width,case,label,fast=True,age=None,save=False,load=None):
        folder=out/f'{width}-{case}-{label}';folder.mkdir();cmd=data['commands'][f'{width}-{case}-lle'].copy();cmd[0]=str(prototype.parent/'player.exe')
        for flag,value in [('--config',out/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if age is not None:cmd[cmd.index('--frames')+1]=str(3894+age)
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        if load:cmd[cmd.index('--load')+1]=str(load)
        env=dict(clean,TLK_FINAL_MD_ART='1',TLK_CONTINUE_BANK_RECORD=str(ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record'),
                 TLK_TITLE_AUDIO_DIR=str(folder),TLK_TITLE_UPLOAD_FAST='1' if fast else '0',TLK_TITLE_UPLOAD_BANK=str(bank),TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[folder.name]=cmd;checks[folder.name+'_exit']=r.returncode==0;print(folder.name,r.returncode,flush=True);return folder
    for width in (256,320):
        for case,original_first in [('no',186),('timeout',890)]:
            control=run(width,case,'control',fast=False)
            previous=source.parent/f'{width}-{case}-lle'
            checks[f'{width}_{case}_control_client']=pixels(control/'window.png')==pixels(previous/'window.png')
            checks[f'{width}_{case}_control_guest']=hashes(control/'run.log')==hashes(previous/'run.log')
            checks[f'{width}_{case}_control_pcm']=pcm(control/'audio.wav')==pcm(previous/'audio.wav')
            fast=run(width,case,'fast')
            checks[f'{width}_{case}_whole_aram']=(fast/'after-aram.bin').read_bytes()==(control/'after-aram.bin').read_bytes()
            checks[f'{width}_{case}_whole_host_driver']=(fast/'after-wram.bin').read_bytes()[0x1f00:0x2000]==(control/'after-wram.bin').read_bytes()[0x1f00:0x2000]
            copies=[r for r in csv.reader((fast/'upload.csv').open()) if r and r[0]=='copy']
            checks[f'{width}_{case}_sixteen_copies']=len(copies)==16 and {int(r[2]) for r in copies}==set(range(16))
            events=[json.loads(line) for line in (fast/'audio.jsonl').read_text().splitlines()];saved=events[0]['age']
            first=next(int(r[1]) for r in csv.reader((fast/'exit.csv').open()) if r[0]=='frame' and r[2]=='c005ab' and int(r[5]))
            observations[f'{width}_{case}']=dict(audio_events=events,first_title=first,original_first_title=original_first,remaining_fields=first-original_first)
            checks[f'{width}_{case}_two_field_upload']=events[1]['age']-events[0]['age']==2
            before=run(width,case,'saved',age=saved,save=True)
            cold=run(width,case,'cold',load=before/'saved.state')
            checks[f'{width}_{case}_cold_client']=pixels(cold/'window.png')==pixels(fast/'window.png')
            checks[f'{width}_{case}_cold_guest']=hashes(cold/'run.log')==hashes(fast/'run.log')
            checks[f'{width}_{case}_cold_pcm']=pcm(cold/'audio.wav')==pcm(fast/'audio.wav')[len(pcm(before/'audio.wav')):]
    paths=[Path(__file__),source,prototype,manifest,bank,ROOT/'tools/pride_title_upload_slice.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                scope='LLE research only; original CPU/SPC completion, cold loads; no compiled/save-identity/public activation',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
