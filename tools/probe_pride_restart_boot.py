"""Observe the actual level-select power-on save in the repeated-revival host."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import environment
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-restart-reproduction';out.mkdir(exist_ok=True)
    build_path=ROOT/'build/pride-repeat/build-report.json'
    build=json.loads(build_path.read_text());binary=ROOT/'build/pride-repeat/repeat-sdl.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    profile=out/'resources.ini';profile.write_bytes((ROOT/'build/pride-repeat/scoped-windows/snes-256-native-aot/resources.ini').read_bytes())
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    boot=out/'tlk_practice_boot.state';assert not boot.exists(),'Use a fresh observation directory'
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--practice-level','0','--frames','2',
             '--no-pace','--no-audio','--no-record','--dump-window',out/'window.png','--dump-png',out/'guest.png']
    with (out/'run.log').open('wb') as log:
        run=subprocess.run(list(map(str,command)),cwd=ROOT,env=environment(out),stdout=log,stderr=subprocess.STDOUT,timeout=90)
    report=dict(result='OBSERVED',exit=run.returncode,boot_state_exists=boot.exists(),guest=hashes(out/'run.log'),
        command=list(map(str,command)),binary_sha256=digest(binary),source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),build_path)},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Power-on state exists:',boot.exists(),'exit:',run.returncode,flush=True)


if __name__=='__main__':main()
