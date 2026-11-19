"""Verify source-tagged native/private saves reject the opposite gameplay choice."""
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-launch2';package_path=base/'preview-package-audit.json';package=bound(package_path);out=base/'save-sources';out.mkdir()
    exe=ROOT/'dist/development-preview/LionKing.exe';assert digest(exe)==package['binary_sha256']
    original=ROOT/'profiles/pride-development-preview.ini';native=out/'snes.ini';native.write_text(original.read_text().replace('gameplay.levels.pride_lands.health_death = md','gameplay.levels.pride_lands.health_death = snes'))
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n');state=out/'native.state';md_state=base/'preview-slots/tlk_slot1.state'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};commands={};checks={}
    common=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--no-pace','--no-audio','--no-record']
    cmd=common+['--resource-profile',native,'--input',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape','--practice-level',0,'--frames',1600,'--save-at',1600,state]
    commands['author-native']=list(map(str,cmd))
    with (out/'author.log').open('wb') as log:r=subprocess.run(commands['author-native'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    assert not r.returncode and state.read_bytes()[:8]==b'TLKSTAT1'
    checks['native_source_bit_clear']=not(int.from_bytes(state.read_bytes()[32:36],'little')&0x20000000)
    data=md_state.read_bytes();assert data[:8]==b'PRPRAC01';inner=int.from_bytes(data[12:16],'little')
    checks['md_source_bit_set']=bool(int.from_bytes(data[inner+32:inner+36],'little')&0x20000000)
    for name,profile,load,message in (('native-into-md',original,state,'Select SNES health death'),('md-into-native',native,md_state,'Select MD health death')):
        before=digest(load);cmd=common+['--resource-profile',profile,'--load',load,'--frames',1700];commands[name]=list(map(str,cmd))
        with (out/(name+'.log')).open('wb') as log:r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
        checks[name+'/rejected']=r.returncode==8 and message in (out/(name+'.log')).read_text()
        checks[name+'/file_preserved']=digest(load)==before
    paths=[Path(__file__),package_path,original,md_state,base/'preview-slots/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                experimental_preview=True,default_installed_player_replaced=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
