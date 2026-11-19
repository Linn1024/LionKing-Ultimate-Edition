"""Preserve nested cache/bank compatibility checks with recomputed checksums."""
import hashlib
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment


def main():
    base=ROOT/'build/pride-save-identity2';build_path=base/'build-report.json';build=bound(build_path);out=base/'nested-rejection';out.mkdir();checks={};commands={};paths=[Path(__file__),build_path]
    def seal(data,at,size,offset):
        data[at+offset:at+offset+32]=bytes(32)
        data[at+offset:at+offset+32]=hashlib.sha256(data[at:at+size]).digest()
    for profile in ('native','md'):
        root=base/'verified'/profile;state=root/'author-a/owned.state';original=state.read_bytes();before=digest(state);assert original[:8]==b'PRHSAVE1';paths.append(state)
        for kind in ('cache','bank'):
            folder=out/(profile+'-'+kind);folder.mkdir();data=bytearray(original)
            cache=data.index(b'PRPREP01');cache_size=int.from_bytes(data[cache+12:cache+16],'little')
            assert data.find(b'PRPREP01',cache+1)==-1 and cache+cache_size<=len(data)
            if kind=='cache':data[cache+16]^=1
            else:
                bank=data.index(b'TLKNBK01',cache);bank_size=int.from_bytes(data[bank+16:bank+20],'little');assert bank+bank_size<=cache+cache_size
                data[bank+24]^=1;seal(data,bank,bank_size,96)
            seal(data,cache,cache_size,48);seal(data,0,len(data),56)
            damaged=folder/'incompatible.state';damaged.write_bytes(data);saved=digest(damaged)
            # Structural/checksum validity is preserved; only the advertised
            # compatibility identity is deliberately invalid.
            view=bytearray(data[cache:cache+cache_size]);expected=bytes(view[48:80]);view[48:80]=bytes(32)
            checks[profile+'/'+kind+'/valid_cache_checksum']=hashlib.sha256(view).digest()==expected
            config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
            cmd=[base/'b.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',root/'resources.ini','--config',config,
                 '--load',damaged,'--frames',2100,'--no-audio','--no-record','--no-pace']
            commands[profile+'/'+kind]=list(map(str,cmd))
            with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[profile+'/'+kind],cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=120)
            checks[profile+'/'+kind+'/identity_rejected']=r.returncode==8 and 'cannot load state ' in (folder/'run.log').read_text()
            checks[profile+'/'+kind+'/all_input_files_preserved']=digest(state)==before and digest(damaged)==saved
    paths.append(ROOT/'tools/verify_pride_live_error_ui.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
