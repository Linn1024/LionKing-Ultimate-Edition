"""Original MD Options difficulty boots followed by ordinary first-attack approach."""
import csv
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab,png
source=ROOT/'build/pride-difficulty-start2/md/report.json';assert bound(source)['result']=='CAPTURED'
movie_path=ROOT/'build/md-next-levels-replay/frames.json';movie=json.loads(movie_path.read_text())
out=ROOT/'build/md-porcupine178-difficulty';out.mkdir()
trace_source=ROOT/'tools/md_porcupine_contact_trace.c';library=out/'trace.dll'
compile=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(trace_source),'-o',str(library)];subprocess.run(compile,check=True)
read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
trace=C.CDLL(str(library));trace.contact_trace_init.argtypes=[C.c_void_p,C.c_char_p]
cases={};paths=[Path(__file__),source,movie_path,trace_source,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'Lion King, The (World).md']
for difficulty,lives in [('easy',9),('normal',3),('hard',1)]:
    folder=out/difficulty;folder.mkdir();prefix_path=source.parent/difficulty/'inputs.json';prefix=json.loads(prefix_path.read_text())
    pads=prefix+[r['pad'] for r in movie[1400:1796]]+[0]*400
    (folder/'inputs.json').write_text(json.dumps(pads)+'\n');game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    assert trace.contact_trace_init(game.core._handle,str(folder/'calls.csv').encode());rows=[]
    try:
        for field,pad in enumerate(pads,1):
            trace.contact_trace_field(field);game.step(pad);game.samples.clear()
            if field<len(prefix):continue
            word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
            player=word(0xcd46+2);valid=0x8000<=player<0xff80
            rows.append(dict(field=field,health=word(0xccf6),lives=word(0xccee),player=[word(player+8),word(player+10)] if valid else None,immunity=word(player+0x46) if valid else None,action=(word(player+0x30)<<16|word(player+0x32))&0xffffff if valid else 0))
            if len(rows)>1 and rows[-1]['health']<rows[-2]['health']:png(folder/f'hit-{field}.png',*game.image)
        png(folder/'final.png',*game.image)
    finally:trace.contact_trace_close();game.close()
    assert rows[0]['health']==4 and rows[0]['lives']==lives,(difficulty,rows[0])
    calls=list(csv.DictReader((folder/'calls.csv').open()));reactions=[r for r in calls if r['pc']=='19a81c' and r['action']=='19a446']
    drops=[dict(field=b['field'],before=a['health'],after=b['health']) for a,b in zip(rows,rows[1:]) if b['health']<a['health']]
    cases[difficulty]=dict(initial=rows[0],drops=drops,reactions=reactions,prefix_fields=len(prefix))
    (folder/'frames.json').write_text(json.dumps(rows,indent=2)+'\n');paths.append(prefix_path)
    print(difficulty,'reactions',len(reactions),'drops',drops,flush=True)
checks=dict(ordinary_options_source_lives_confirmed=True,all_three_have_original_porcupine_reactions=all(r['reactions'] for r in cases.values()))
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if all(checks.values()) else 'NO_ATTRIBUTED_HIT',checks=checks,cases=cases,compile_command=compile,
    scope='Original MD real Options difficulty prefixes, ordinary recorded approach then neutral. Read-only original attack/reaction trace; no actor, difficulty-memory, health or ROM edits. Source timings/histories remain separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('CAPTURED' if all(checks.values()) else 'NO_ATTRIBUTED_HIT',checks,flush=True)
