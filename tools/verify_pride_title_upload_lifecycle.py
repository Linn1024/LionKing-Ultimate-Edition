"""Verify research upload whole-ARAM result, cold CPU/SPC continuation and next game."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm

def main():
    base=ROOT/'build/pride-title-upload-prototype5';control=base/'report.json';original=bound(control)
    source=ROOT/'build/pride-title-upload-fast5/report.json';data=bound(source)
    life=ROOT/'build/pride-game-over13/lifecycle2/report.json';lifecycle=bound(life)
    package=ROOT/'build/pride-title-bank-installed/setup-verification/Game data & title bank/install.json';info=json.loads(package.read_text());bank=package.parent/info['title_bank_assets']['file']
    out=ROOT/'build/pride-title-upload-lifecycle5';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(width,label,age,load=None,save=False,tape=None):
        folder=out/f'{width}-{label}';folder.mkdir();cmd=data['commands'][str(width)].copy()
        for flag,value in [('--config',out/'host.ini'),('--frames',4444+age),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if tape:cmd[cmd.index('--input')+1]=str(tape)
        if save:cmd+=['--save-at',str(4444+age),str(folder/'saved.state')]
        actual=dict(env,TLK_FINAL_MD_ART='1',TLK_TITLE_AUDIO_DIR=str(folder),TLK_TITLE_UPLOAD_FAST='1',TLK_TITLE_UPLOAD_BANK=str(bank),TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[folder.name]=cmd;checks[folder.name+'_exit']=r.returncode==0;print(folder.name,r.returncode,flush=True);return folder
    def same(prefix,a,b,skip=0):
        checks[prefix+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[prefix+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[prefix+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    for width in (256,320):
        fast=source.parent/str(width)
        checks[f'{width}_whole_aram_matches_original']=(fast/'after-aram.bin').read_bytes()==(base/str(width)/'after-aram.bin').read_bytes()
        prefix=ROOT/f'build/pride-title-native15/verification/{width}-366/audio.wav'
        checks[f'{width}_pcm_before_upload_preserved']=pcm(fast/'audio.wav')[:len(pcm(prefix))]==pcm(prefix)
        frames={}
        for age in (367,368,372):frames[age]=run(width,str(age),age,save=age!=372)
        for saved,target in ((367,372),(368,372),(367,700)):
            cold=run(width,f'cold{saved}to{target}',target,load=frames[saved]/'saved.state')
            same(f'{width}_cold{saved}to{target}',cold,frames[372] if target==372 else fast,len(pcm(frames[saved]/'audio.wav')))
        tape=Path(lifecycle['commands'][f'{width}-new-game2000'][lifecycle['commands'][f'{width}-new-game2000'].index('--input')+1])
        live=run(width,'new-game2000',2000,tape=tape,save=True)
        cold=run(width,'cold-new-game2000',2000,load=frames[367]/'saved.state',tape=tape)
        same(f'{width}_cold_next_game',cold,live,len(pcm(frames[367]/'audio.wav')))
        scene=json.loads((live/'scene.json').read_text());g=scene['latched_gameplay']
        checks[f'{width}_next_game_is_pride']=scene['level']==0 and g['descriptor']==0x387 and g['health']==4
        checks[f'{width}_native_new_game_counters']=all(g[k]==lifecycle['observations'][str(width)]['native_control'][k] for k in ('health','lives','player','checkpoint'))
        raw=(live/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
        checks[f'{width}_owner_retired']=struct.unpack_from('<I',raw,at+100)[0]==struct.unpack_from('<I',raw,at+112)[0]==0
        rows=list(csv.reader((live/'upload.csv').open()));copies=[r for r in rows if r and r[0]=='copy']
        checks[f'{width}_only_title_sixteen_copies']=len(copies)==16 and {int(r[2]) for r in copies}==set(range(16))
        observations[str(width)]=dict(next_game=g,fields_saved=63,scope='LLE research; fast flag/package are not yet part of save identity; compiled integration and early title Start remain open')
    paths=[Path(__file__),source,control,life,package,bank,ROOT/'tools/pride_title_upload_slice.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                scope='Research LLE cold continuation and next game only; no public/compiled/capability promotion',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
