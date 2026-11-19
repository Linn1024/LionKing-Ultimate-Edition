"""Observe boot/final destination decoder calls without changing their work."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-final-preparation-probe';out=base/'capture';out.mkdir()
    build=bound(base/'build-report.json');binary=base/'player.exe';assert digest(binary)==build['binary_sha256']
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    state=ROOT/'build/pride-final-presentation/preview/prefatal.state'
    tape=ROOT/'build/pride-final-presentation/preview/ordinary.tape'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];observations={};checks={}
    for name in ('boot','final'):
        folder=out/name;folder.mkdir()
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--lle','--frames',600 if name=='boot' else 2489,
             '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png']
        if name=='final':cmd+=['--input',tape,'--load',state]
        commands.append(list(map(str,cmd)))
        env=dict(clean,TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_FINAL_SKIP='0',
                 TLK_FINAL_LATE_SKIP='1' if name=='final' else '0',TLK_FINAL_DECODE_FOLDER=str(folder))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        rows=list(csv.DictReader((folder/'decoder.csv').open()));observations[name]=rows
        if name=='final':
            reference=ROOT/'build/pride-late-visible/120'
            checks['observer_retains_late_client']=pixels(folder/'window.png')==pixels(reference/'window.png')
            checks['observer_retains_late_gameplay']=hashes(folder/'run.log')==hashes(reference/'run.log')
        else:
            reference=json.loads((ROOT/'build/pride-reset/fixed4/native/gates/play-report.json').read_text())['routes']['idle600']['aot']
            checks['observer_retains_native_boot']=hashes(folder/'run.log')==reference
        print(name,rows,flush=True)
    paths=[Path(__file__),base/'build-report.json',binary,state,tape]
    report=dict(result='OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        decoder_instructions_unchanged=True,excluded_late_bypass_only=True,public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'final destination decoder observation',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
