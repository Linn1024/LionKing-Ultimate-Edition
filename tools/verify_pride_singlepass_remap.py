"""Run both staged frontends' actual SDL input/menu remap self-test."""
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-singlepass';out=base/'remap';out.mkdir();checks={};commands={};builds={};paths=[Path(__file__)]
    for name,folder,filename in (('mixed',base,'singlepass.exe'),('native',base/'plain-native','native.exe')):
        build_path=folder/'build-report.json';build=bound(build_path);binary=folder/filename;assert digest(binary)==build['binary_sha256'];builds[name]=build['binary_sha256'];paths.append(build_path)
        case=out/name;case.mkdir();profile=case/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--config',case/'host.ini','--resource-profile',profile,'--no-audio','--no-record','--selftest-remap'];commands[name]=list(map(str,cmd))
        env=os.environ.copy();env['SDL_VIDEODRIVER']='dummy'
        with (case/'run.log').open('wb') as log:r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
        checks[name+'/exit']=r.returncode==0;checks[name+'/selftest']='remap_selftest: PASS (0 failed)' in (case/'run.log').read_text()
    assert all(checks.values()),checks
    report=dict(result='PASS',checks=checks,commands=commands,binaries_sha256=builds,source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS remap',checks,flush=True)


if __name__=='__main__':main()
