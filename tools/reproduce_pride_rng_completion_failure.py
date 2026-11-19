"""Retain both modes and diagnostics for the new full-mixture route failure."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player';bp=base/'build-report.json';build=bound(bp);out=base/'completion-failure';out.mkdir()
    profile=base/'completion/320/resources.ini';tape=ROOT/'build/pride-normal-completion/route.polled.tape';commands={};results={}
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir();cfg=folder/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
        cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',cfg,'--input-polled',tape,'--frames',4700,'--no-pace','--no-audio','--no-record',
             '--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,4701)))]
        if mode=='lle':cmd+=['--lle']
        commands[mode]=list(map(str,cmd));child=dict(env,TLK_PRIDE_DIAGNOSTICS=str(folder),TLK_RNG_ENTRY_TRACE=str(folder/'entry.csv'))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[mode],cwd=ROOT,env=child,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        rows=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text())
        results[mode]=dict(exit=r.returncode,last_field=int(rows[-1][0]) if rows else None);print(mode,results[mode],flush=True)
        for p in folder.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
    paths=[Path(__file__),bp,profile,tape]
    report=dict(result='CAPTURED',runs=results,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        full_mixture_completion_verified=False,full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
