"""Observe native RNG lifecycle, comparing each run with its unchanged host."""
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import hashes


def main():
    base=ROOT/'build/pride-rng-lifecycle';bp=base/'build-report.json';build=bound(bp);out=base/'native';out.mkdir();checks={};commands={}
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    cases=[('completion',ROOT/'engine/tapes/allbugsF.read.tape',5000,True),
           ('checkpoint',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',5400,True),
           ('continue',ROOT/'build/pride-game-over-music/normal.tape',5500,False)]
    paths=[Path(__file__),bp];clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for name,tape,frames,polled in cases:
        root=out/name;root.mkdir();paths.append(tape)
        for version,exe in (('control',ROOT/'engine/build-win/tlk_headless.exe'),('observer',base/'observer.exe')):
            cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--lle','--frames',frames,
                 '--input-polled' if polled else '--input',tape,'--ram-log',root/(version+'.ram')]
            env=dict(clean)
            if version=='observer':env['TLK_RNG_OBSERVE']=str(root/'rng.csv')
            commands[name+'/'+version]=list(map(str,cmd))
            with (root/(version+'.log')).open('wb') as log:subprocess.run(commands[name+'/'+version],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        checks[name+'/every_tracked_field']=(root/'control.ram').read_bytes()==(root/'observer.ram').read_bytes()
        checks[name+'/final_full_guest_hashes']=hashes(root/'control.log')==hashes(root/'observer.log') and len(hashes(root/'control.log'))==2
        print(name,[k for k,v in checks.items() if not v],flush=True)
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},production_changed=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
