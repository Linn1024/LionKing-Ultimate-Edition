"""Adapt ordinary menu inputs of the credited route; never change guest state.

Source route inherits ShgofcTAS All Bugs Final (CC BY2.0), credited in
docs/pride-lands-status.md. Derived recordings stay under ignored build/.
"""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--insert',type=int,default=0);parser.add_argument('--frames',type=int,default=1200);args=parser.parse_args()
    base=ROOT/'build/pride-restart-prefix-observer26';bound(base/'build-report.json')
    source=ROOT/'build/pride-restart-difficulty25/completion/report.json';old=bound(source)
    out=ROOT/('build/pride-restart-prefix-adapt'+str(args.insert));out.mkdir()
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    template=old['commands']['256-md'];original=Path(template[template.index('--input-polled')+1]);data=bytearray(original.read_bytes())
    struct.pack_into('<H',data,484*2,0x80)  # An ordinary Options A instead of early confirmation.
    boundary=638*2;data[boundary:boundary]=bytes(args.insert*2)
    tape=out/'ordinary.polled.tape';tape.write_bytes(data)
    cmd=template.copy();cmd[0]=str(base/'player.exe')
    for flag,value in [('--input-polled',tape),('--frames',args.frames),('--config',out/'host.ini'),('--dump-window',out/'window.png'),
                       ('--dump-scene',out/'scene.json'),('--wav',out/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    with (out/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1',TLK_SOFT_TREE_LOG=str(out/'tree.jsonl')),
        stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    rows=[json.loads(line) for line in (out/'tree.jsonl').read_text().splitlines()]
    first=next((row for row in rows if row['descriptor']==0xc00387 and row['level']==0),None)
    scene=json.loads((out/'scene.json').read_text())
    checks=dict(exit=r.returncode==0,easy_selected=first is not None and first['difficulty']==0,
                gameplay_suffix_unchanged=data[boundary+args.insert*2:]==original.read_bytes()[boundary:])
    observations=dict(first_pride=first,final_level=scene['level'],inserted_neutral_polls=args.insert,changed_menu_poll=484)
    paths=[Path(__file__),source,base/'build-report.json',original]
    report=dict(result='OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,command=cmd,
                ordinary_inputs=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],{k:first.get(k) if first else None for k in ('field','poll_index','difficulty')},'final level',scene['level'],flush=True)


if __name__=='__main__':main()
