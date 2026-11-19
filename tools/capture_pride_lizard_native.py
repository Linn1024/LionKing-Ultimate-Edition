"""Capture current native active-list history on the paired ordinary-input route."""
import json
import os
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-lizard-history/native';out.mkdir(parents=True)
    reference=ROOT/'build/pride-ground-gap/native';exe=ROOT/'engine/build-win/tlk_headless.exe'
    profile=reference/'resources.ini';tape=reference/'derived.polled.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_WRAM_DUMP=','.join(map(str,range(950,1633))),TLK_WRAM_DIR=str(out))
    cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
         '--input-polled',tape,'--frames',1632,'--ram-log',out/'game.ram']
    with (out/'run.log').open('wb') as log:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    rows=[]
    for field in range(950,1633):
        ram=(out/f'hl_wram_{field}.bin').read_bytes();word=lambda at:struct.unpack_from('<H',ram,at)[0]
        if word(0x1ff9e) or word(0xdf) not in (0x387,0x80d):continue
        actors=[];at=0xb213;previous=0
        while at:
            assert 0x8000<=at<=0xff80 and len(actors)<80 and word(at)==previous,(field,at)
            words=list(struct.unpack_from('<64H',ram,at));actors.append(dict(actor=at,words=words));previous,at=at,words[1]
        rows.append(dict(field=field,player=[word(0xb21b),word(0xb21d)],actors=actors))
    (out/'actors.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    paths=[Path(__file__),exe,profile,tape,reference/'early-audit.json']
    report=dict(result='CAPTURED',fields=len(rows),command=list(map(str,cmd)),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},guest_mutated=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Captured',len(rows),'current active-list fields',flush=True)


if __name__=='__main__':main()
