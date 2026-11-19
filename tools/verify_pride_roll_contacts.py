"""Check execution parity on longer chase fixtures, retaining MD fidelity gaps."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'build/pride-roll-grid-fixed')
    parser.add_argument('--out',type=Path,default=ROOT/'build/pride-roll-contact-parity')
    args=parser.parse_args()
    source=args.source;capture=json.loads((source/'snes.json').read_text())
    host=ROOT/'engine/build-win/tlk_headless.exe'
    assert (source/'snes.json').stat().st_mtime>=host.stat().st_mtime
    assert capture['md_camera_selected'] and capture['md_start_selected'] and capture['ordinary_native_input_boot']
    assert hashlib.sha256((source/'ready-native.state').read_bytes()).hexdigest()==capture['ready_checkpoint_sha256']
    out=args.out;out.mkdir(parents=True,exist_ok=True);results={}
    for name,rows in capture['cases'].items():
        folder=out/name;folder.mkdir(exist_ok=True);baseline=source/name/'snes'
        env=os.environ.copy();env.update(TLK_WRAM_DUMP=','.join(str(2457+i) for i in range(len(rows))),TLK_WRAM_DIR=str(folder))
        cmd=[host,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',source/'native.ini','--load',source/'ready-native.state','--frames',2456+len(rows),
             '--input',baseline/'input.tape']
        log=folder/'game.log'
        with log.open('wb') as stream:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
        for i in range(len(rows)):
            file=f'hl_wram_{2457+i}.bin';assert (folder/file).read_bytes()==(baseline/file).read_bytes(),(name,i,'full AOT/LLE WRAM differs')
        assert hashes(log)==hashes(baseline/'game.log') and len(hashes(log))==2
        results[name]={'fields':len(rows),'hashes':hashes(log)};print(name,'full AOT/LLE identity PASS; original comparison is separate',flush=True)
    report={'result':'PASS','scope':__doc__,'cases':results,'fields':sum(len(r) for r in capture['cases'].values()),
            'headless_sha256':hashlib.sha256(host.read_bytes()).hexdigest(),
            'capture_sha256':hashlib.sha256((source/'snes.json').read_bytes()).hexdigest(),
            'original_md_fidelity_proven':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
