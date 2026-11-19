"""Check original MD Sun observations against a pad-only observer control."""
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    source_report=ROOT/'build/md-continue-token-original2/report.json';prior=bound(source_report);assert prior['result']=='PASS'
    out=source_report.parent/'qualification';out.mkdir()
    source=ROOT/'tools/md_continue_token_trace3.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)],check=True)
    trace=C.CDLL(str(library));trace.pickup_flight_init.argtypes=[C.c_void_p,C.c_char_p]
    trace.pickup_flight_observe.argtypes=[C.c_int]
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2';pads,_,settings=movie_inputs(movie)
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    with reference.open() as f:polled=[pads[int(r['frame'])-1] for r in csv.DictReader(f) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    runs={}
    for label,observe in [('pad-only-control',0),('sun-observer',1)]:
        folder=out/label;folder.mkdir();game=MdLab()
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
        assert trace.pickup_flight_init(game.core._handle,str(folder/'calls.csv').encode())
        trace.pickup_flight_observe(observe);index=0
        try:
            with (folder/'fields.jsonl').open('w') as log:
                for field in range(1,3501):
                    trace.pickup_flight_field(field);game.step(polled[index])
                    if trace.pickup_flight_polled():index+=1
                    row=dict(field=field,polls=index,wram=hashlib.sha256(bytes(game.work_ram)).hexdigest(),video=hashlib.sha256(game.image[0]).hexdigest(),geometry=game.image[1:])
                    log.write(json.dumps(row,separators=(',',':'))+'\n')
            (folder/'audio.pcm').write_bytes(game.samples);(folder/'final-ram.bin').write_bytes(bytes(game.work_ram));png(folder/'final.png',*game.image)
            runs[label]=dict(polls=index,fields=3500)
        finally:trace.pickup_flight_close();game.close()
    a=out/'pad-only-control';b=out/'sun-observer'
    checks={name+'_neutral':digest(a/name)==digest(b/name) for name in ('fields.jsonl','audio.pcm','final-ram.bin','final.png')}
    checks['ordinary_poll_schedule_preserved']=runs['pad-only-control']['polls']==runs['sun-observer']['polls']==prior['input_polls']
    checks['retained_sun_calls_reproduced']=digest(b/'calls.csv')==digest(source_report.parent/'calls.csv')
    checks['control_no_sun_logging']=len((a/'calls.csv').read_text().splitlines())==1
    paths=[Path(__file__),source,library,source_report,movie,reference,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,runs=runs,
                no_guest_edits=True,control_still_observes_pad_reads=True,no_fresh_external_emulator_claim=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
