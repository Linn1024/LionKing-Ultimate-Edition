"""Retain the actual cold private-load failure and read-only nested preflight."""
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player2';observer=base/'save-validator'
    bp=observer/'build-report.json';build=bound(bp);assert digest(observer/'player.exe')==build['binary_sha256']
    out=base/'cold-private-failure';out.mkdir();profile=base/'completion-reference-unpaused256/256/resources.ini'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    paths=[Path(__file__),bp,profile];cases={};commands={}
    for parent in ('width-plan1','width-plan2'):
        state=base/parent/'anchor/end.state';tape=base/parent/'d1-p0-L.polled.tape'
        before=digest(state);paths.extend([state,tape])
        for mode in ('aot','lle'):
            name=parent+'-'+mode;folder=out/name;folder.mkdir()
            config=folder/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
            env=dict(clean,SDL_VIDEODRIVER='dummy',TLK_SAVE_VALIDATION_LOG=str(folder/'validation.log'))
            cmd=[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--config',config,'--input-polled',tape,'--load',state,
                 '--frames',1470,'--no-pace','--no-audio','--no-record']
            if mode=='lle':cmd+=['--lle']
            commands[name]=list(map(str,cmd))
            with (folder/'run.log').open('wb') as log:
                result=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
            cases[name]=dict(exit=result.returncode,state_preserved=digest(state)==before,
                validation=(folder/'validation.log').read_text() if (folder/'validation.log').exists() else None)
            print(name,cases[name],flush=True)
    report=dict(result='CAPTURED',cases=cases,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
