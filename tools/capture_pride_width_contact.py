"""Copy active actors and exact input indices around the first width-dependent hit."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player2';observer=base/'width-observer'
    bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    out=base/'width-contact';out.mkdir();frames=[930,971,972,1350,1375,*range(1398,1406)]
    tape=base/'controller-unpaused2/route.polled.tape'
    parents={320:base/'completion-reference-unpaused2/320',256:base/'completion-reference-unpaused256/256'}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def run(width):
        folder=out/str(width);folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
        env=dict(clean,SDL_VIDEODRIVER='dummy',TLK_OBS_DUMP_FIELDS=','.join(map(str,frames)),TLK_OBS_DUMP_DIR=str(folder),
                 TLK_TRACKED_RAM_LOG=str(folder/'route.ram'),TLK_CAMERA_TRACE=str(folder/'camera.csv'))
        cmd=[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',parents[width]/'resources.ini','--config',config,'--input-polled',tape,
             '--frames',1405,'--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,1406)))]
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert result.returncode==0,result.returncode
        rows=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(parents[width]/'aot/run.log').read_text())[:1405]
        assert len(rows)==1405 and rows==expected,('Observer changed guest',width)
        snapshots=[]
        for frame in frames:
            ram=(folder/f'wram-{frame}.bin').read_bytes();assert len(ram)==0x20000
            word=lambda at:struct.unpack_from('<H',ram,at)[0]
            actors=[];at=0xb213;previous=0
            while at:
                assert 0x8000<=at<=0xff80 and len(actors)<80 and word(at)==previous,(width,frame,at)
                words=list(struct.unpack_from('<64H',ram,at));actors.append(dict(actor=at,words=words));previous,at=at,words[1]
            snapshots.append(dict(field=frame,player=[word(0xb21b),word(0xb21d)],health=word(0x2004),
                                  contact=word(0xb237),camera=[word(0xb29b),word(0xb29d)],actors=actors))
        (folder/'actors.json').write_text(json.dumps(snapshots,indent=2)+'\n')
        return list(map(str,cmd))
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs={w:pool.submit(run,w) for w in (256,320)};commands={str(w):f.result() for w,f in jobs.items()}
    paths=[Path(__file__),bp,tape,*[p/'resources.ini' for p in parents.values()],*[p/'aot/run.log' for p in parents.values()]]
    report=dict(result='CAPTURED',commands=commands,observer_full_frame_wram_neutral_every_field=True,compared_fields=2810,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        guest_mutated=False,full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Captured both widths;2810 observed fields exact',flush=True)


if __name__=='__main__':main()
