"""Try ordinary roar/jump controls around the first narrow-view porcupine hit."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player2';observer=base/'width-observer'
    bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    out=base/'width-controls';out.mkdir()
    original=base/'controller-unpaused2/route.polled.tape'
    raw=original.read_bytes();initial=list(struct.unpack('<'+'H'*(len(raw)//2),raw))
    profile=base/'completion-reference-unpaused256/256/resources.ini'
    cases={}
    for at in (1055,1065,1073,1080,1090):
        values=initial.copy()
        for i in range(at,at+6):values[i]|=0x80
        cases[f'roar-{at}']=values
    for hold in (8,12,24):
        values=initial.copy()
        for i in range(1073,1104):values[i]=(values[i]&~0x8000)|(0x8000 if i<1073+hold else 0)
        cases[f'jump-{hold}']=values
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    def run(name,values):
        folder=out/name;folder.mkdir();tape=folder/'route.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
        env=dict(clean,SDL_VIDEODRIVER='dummy',TLK_OBS_DUMP_FIELDS='1430',TLK_OBS_DUMP_DIR=str(folder),TLK_TRACKED_RAM_LOG=str(folder/'route.ram'))
        cmd=[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',1430,
             '--no-pace','--no-audio','--no-record']
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert result.returncode==0,(name,result.returncode)
        ram=(folder/'wram-1430.bin').read_bytes();word=lambda at:struct.unpack_from('<H',ram,at)[0]
        tracked=[r.split() for r in (folder/'route.ram').read_text().splitlines()]
        entry=dict(player=[word(0xb21b),word(0xb21d)],health=word(0x2004),lives=word(0x1ffaa),
                   health_loss_fields=[int(b[0]) for a,b in zip(tracked,tracked[1:]) if int(b[0])>1000 and int(a[3],16)>int(b[3],16)],
                   tape=tape.relative_to(ROOT).as_posix(),tape_sha256=digest(tape),command=list(map(str,cmd)))
        print(name,entry['player'],entry['health'],entry['health_loss_fields'],flush=True)
        return entry
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs={name:pool.submit(run,name,values) for name,values in cases.items()};results={name:f.result() for name,f in jobs.items()}
    paths=[Path(__file__),bp,original,profile]
    report=dict(result='CAPTURED',cases=results,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        ordinary_poweron_controller_inputs_only=True,loaded_states=False,guest_mutated=False,
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
