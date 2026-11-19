"""Evaluate ordinary narrow-view controls from boot using a read-only observer."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tape',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--frames',type=int,default=6000)
    args=parser.parse_args();tape=args.tape.resolve();out=args.out.resolve();out.mkdir()
    base=ROOT/'build/pride-rng-player2';observer=base/'width-observer'
    bp=observer/'build-report.json';build=bound(bp);assert digest(observer/'player.exe')==build['binary_sha256']
    profile=base/'completion-reference-unpaused256/256/resources.ini'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(SDL_VIDEODRIVER='dummy',TLK_OBS_DUMP_FIELDS=str(args.frames),TLK_OBS_DUMP_DIR=str(out),
               TLK_TRACKED_RAM_LOG=str(out/'route.ram'))
    cmd=[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
         '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',args.frames,
         '--no-pace','--no-audio','--no-record']
    with (out/'run.log').open('wb') as log:
        result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
    assert result.returncode==0,result.returncode
    ram=(out/f'wram-{args.frames}.bin').read_bytes();word=lambda at:struct.unpack_from('<H',ram,at)[0]
    tracked=[r.split() for r in (out/'route.ram').read_text().splitlines()]
    active=[r for r in tracked if int(r[0])>1000 and int(r[6],16)==0]
    transition=next((int(r[0]) for r in tracked if int(r[0])>1000 and int(r[6],16)==1),None)
    observations=dict(player=[word(0xb21b),word(0xb21d)],health=word(0x2004),lives=word(0x1ffaa),
        level=word(0x1ff9e),first_next_level_field=transition,
        minimum_pride_y=min(int(r[5],16) for r in active),
        life_loss_fields=[int(b[0]) for a,b in zip(active,active[1:]) if int(a[7],16)>int(b[7],16)])
    paths=[Path(__file__),bp,tape,profile]
    report=dict(result='CAPTURED',observations=observations,command=list(map(str,cmd)),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        ordinary_poweron_controller_inputs_only=True,loaded_states=False,guest_mutated=False,
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(observations,flush=True)


if __name__=='__main__':main()
