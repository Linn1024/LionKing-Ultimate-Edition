"""Reuse completed167 captures and parse the host's bit-reversed joypad format."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
old=ROOT/'build/pride-contact167-current';attempt=old/'attempt-report.json';assert not attempt.exists()
verifier_source=Path(__file__).with_name('capture_pride_contact167_current.py')
shutil.copy2(verifier_source,old/'capture-script-attempt1.py')
attempt.write_text(json.dumps(dict(result='FAIL',reason='All seed/first-branch players exited0. Parser compared raw SNES tape bits with host-normalized joypad bits; Right0100 is host0080. No guest input or game change.',
    source_sha256={'tools/capture_pride_contact167_current.py':digest(verifier_source)},artifacts_sha256={p.relative_to(old).as_posix():digest(p) for p in old.rglob('*') if p.is_file()}),indent=2)+'\n')
source=verifier_source.read_text().replace("ROOT/'build/pride-contact167-current'","ROOT/'build/pride-contact170-current'")
before="""seed=out/'current.state'
control=run('seed-production',base/'player.exe',2456,prefix,True,save=seed)
pilot=run('seed-observer',observer/'player.exe',2456,prefix,True,first=2456)"""
after="""prior_capture=ROOT/'build/pride-contact167-current'
seed=prior_capture/'current.state'
control=prior_capture/'seed-production'
pilot=prior_capture/'seed-observer'"""
assert source.count(before)==1;source=source.replace(before,after)
oldrun="folder=run(name,observer/'player.exe',2456+len(pads),tape,load=seed)"
newrun="folder=prior_capture/name if name=='long-roll-chase' else run(name,observer/'player.exe',2456+len(pads),tape,load=seed)"
assert source.count(oldrun)==1;source=source.replace(oldrun,newrun)
source=source.replace("assert field==2457+n and pad==pads[n],","assert field==2457+n and pad==(int(format(pads[n],'016b')[::-1],2)&0x0fff),")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,attempt,seed,ROOT/"engine/snesrecomp/runner/src/snes/joypad.c",*[p for p in prior_capture.rglob("*") if p.is_file()],')
exec(compile(source,str(verifier_source),'exec'))
