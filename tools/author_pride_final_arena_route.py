"""Reach a last-life hyena hit using the ordinary hard route and walking inputs."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    plan=ROOT/'build/pride-native-hyena-hard-repeat-plan';source=plan/'report.json';bound(source)
    out=ROOT/'build/pride-final-arena-route2';out.mkdir()
    used=int(re.search(r'tape_words_used=(\d+)',(plan/'anchor/run.log').read_text()).group(1))
    prefix=(plan/'selected.polled.tape').read_bytes()[:used*2]
    suffix=([0x200]*24+[0x100]*24)*70
    tape=out/'ordinary.polled.tape';tape.write_bytes(prefix+struct.pack('<'+'H'*len(suffix),*suffix))
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    exe=ROOT/'engine/build-win/tlk_headless.exe'
    common=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--input-polled',tape]
    with (out/'run.log').open('wb') as log:
        subprocess.run(list(map(str,common+['--frames',6000,'--ram-log',out/'ram.log'])),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    rows=[r.split() for r in (out/'ram.log').read_text().splitlines()]
    fatal=next(int(r[0]) for r in rows if int(r[0])>4000 and int(r[3],16)==0 and int(r[6],16)==0)
    local=dict(env,TLK_WRAM_DUMP=str(fatal),TLK_WRAM_DIR=str(out))
    with (out/'fatal.log').open('wb') as log:
        subprocess.run(list(map(str,common+['--frames',fatal,'--dump-png',out/'fatal.png'])),cwd=ROOT,env=local,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    ram=(out/f'hl_wram_{fatal}.bin').read_bytes();word=lambda a:struct.unpack_from('<H',ram,a)[0]
    assert word(0xdf)==0x80d and word(0x2004)==word(0x1ffaa)==0
    paths=[Path(__file__),source,plan/'selected.polled.tape',plan/'anchor/run.log',exe,ROOT/'Lion King, The (USA).sfc']
    report=dict(result='AUTHORED',ordinary_power_on=True,guest_or_rom_edits=False,fatal_field=fatal,
        descriptor=hex(word(0xdf)),difficulty=word(0x1ff92),position=[word(0xb21b),word(0xb21d)],
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Ordinary arena final',fatal,report['position'],flush=True)


if __name__=='__main__':main()
