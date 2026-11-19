"""Exercise a native save before the APU has acquired its absolute port clock."""
import json
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes


def main():
    base=ROOT/'build/pride-restart-clock/native';out=base/'early-state';out.mkdir(exist_ok=True)
    build_path=base/'build-report.json';build=json.loads(build_path.read_text());binary=base/'native-headless.exe'
    assert digest(binary)==build['runs']['headless']['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    commands={}
    def run(name,mode,frames,extra=()):
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--frames',frames]+list(extra)
        if mode=='lle':command+=['--lle']
        commands[name]=list(map(str,command))
        with (out/(name+'.log')).open('wb') as log:
            r=subprocess.run(commands[name],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        assert not r.returncode,(name,r.returncode)
        return hashes(out/(name+'.log'))
    checks={};state=out/'frame1.state'
    run('seed','aot',1,['--save-at',1,state])
    data=state.read_bytes();assert data[:8]==b'TLKSTAT1'
    blob=data[36:36+struct.unpack_from('<Q',data,24)[0]]
    marker=struct.pack('<I',0x49425253);assert blob.count(marker)==1
    # Windows MinGW layout: existing fields through512 bytes of dynamic values
    # end at584; the appended u64 uses the previously zero-filled bridge tail.
    at=blob.index(marker);remainder=struct.unpack_from('<Q',blob,at+584)[0]
    checks['nonzero_fraction_saved']=0<remainder<21442080
    baseline={}
    for mode in ('aot','lle'):
        baseline[mode]=run('baseline-'+mode,mode,6000)
        resumed=run('resumed-'+mode,mode,6000,['--load',state])
        checks[mode+'/resume']=resumed==baseline[mode]
    checks['baseline_modes']=baseline['aot']==baseline['lle']
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),build_path,ROOT/'tools/verify_windows.py')}
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,saved_remainder=remainder,
        binary_sha256=digest(binary),source_sha256=sources,commands=commands,
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'early fractional state',remainder,checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
