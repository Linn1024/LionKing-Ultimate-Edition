"""Reproduce the old shared temporary-file race against the corrected player."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    old=ROOT/'build/pride-rng-player2';new=ROOT/'build/pride-rng-player3'
    bp=new/'build-report.json';build=bound(bp);assert digest(new/'player.exe')==build['binary_sha256']
    out=new/'shared-save-race';out.mkdir()
    state=old/'width-plan2/anchor/end.state';before=digest(state)
    tape=old/'width-plan2/d1-p0-L.polled.tape';profile=old/'completion-reference-unpaused256/256/resources.ini'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};clean['SDL_VIDEODRIVER']='dummy'
    commands={};cases={}
    def run(generation,index):
        label=f'{generation}-{index}';folder=out/label;folder.mkdir()
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        binary=(old if generation=='old' else new)/'player.exe'
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input-polled',tape,'--load',state,
             '--frames',1470,'--no-pace','--no-audio','--no-record']
        if index%2:cmd+=['--lle']
        commands[label]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(commands[label],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=90)
        text=(folder/'run.log').read_text()
        hashes=dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',text,re.M))
        return dict(exit=result.returncode,hashes=hashes)
    for generation in ('old','new'):
        with ThreadPoolExecutor(max_workers=8) as pool:
            jobs={i:pool.submit(run,generation,i) for i in range(16)}
            cases[generation]={str(i):f.result() for i,f in jobs.items()}
    failures=[k for k,v in cases['old'].items() if v['exit']]
    reference=next(v['hashes'] for v in cases['old'].values() if not v['exit'])
    checks=dict(old_failure_reproduced=bool(failures),all_new_loads_succeed=all(not v['exit'] for v in cases['new'].values()),
        all_new_guest_endpoints_exact=all(v['hashes']==reference for v in cases['new'].values()),original_save_preserved=digest(state)==before)
    paths=[Path(__file__),bp,old/'build-report.json',state,tape,profile]
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,commands=commands,
        original_failures=failures,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'old failed',len(failures),'new failed',sum(bool(v['exit']) for v in cases['new'].values()),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
