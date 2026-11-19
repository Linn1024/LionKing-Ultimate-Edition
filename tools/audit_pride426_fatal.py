"""One ordinary MD fatal-hit episode: selected action versus displayed pose.

Run with .tools/python32/python.exe. No guest/ROM edits, no state loads and no
replacement callees. A read-only CPU hook observes the existing recorded route.
"""
import csv,ctypes as C,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
out=ROOT/'build/pride426-fatal';out.mkdir(exist_ok=True)
source=ROOT/'tools/pride_fatal_trace426.c';dll=out/'trace.dll'
cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(dll)]
subprocess.run(cmd,cwd=ROOT,check=True)
reference=ROOT/'build/pride-death-timeline/md';report=json.loads((reference/'report.json').read_text());assert report['result']=='PASS'
baseline={r['frame']:r for r in json.loads((reference/'samples.json').read_text())}
inputs=ROOT/'build/md-next-levels-replay/frames.json';pads=json.loads(inputs.read_text())
for key,path in (('samples',reference/'samples.json'),('input',inputs),('core',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll')):assert digest(path)==report['source_sha256'][key]
read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
game=MdLab();trace=C.CDLL(str(dll));trace.fatal_trace_init.argtypes=[C.c_void_p,C.c_char_p]
assert trace.fatal_trace_init(game.core._handle,str(out/'events.csv').encode())
game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
for port in (0,1):game.core.retro_set_controller_port_device(port,513)
word=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
rows=[];matched=0
try:
    for frame in range(1,4786):
        trace.fatal_trace_frame(frame);game.step(pads[frame-1]['pad'] if frame<=4000 else 0)
        if frame>=4700:
            camera=word(0xcd36);actor=word(camera+36);draw=word(actor+12)
            r=dict(frame=frame,health=word(0xccf6),xy=[word(actor+8),word(actor+10)],words=[word(actor+i*2) for i in range(64)],pose=(word(draw+10)<<16|word(draw+12))&0xffffff)
            original=baseline[frame];assert all(r[k]==original[k] for k in r);matched+=1;rows.append(r)
        if frame in (4754,4755,4759,4779):png(out/(str(frame)+'.png'),*game.image)
        game.samples.clear()
finally:trace.fatal_trace_close();game.close()
events=list(csv.DictReader((out/'events.csv').open()))
fatal=next(r['frame'] for i,r in enumerate(rows) if i and r['health']==0 and rows[i-1]['health']>0)
episode=[r for r in events if int(r['frame'])==fatal]
(out/'samples.json').write_text(json.dumps(rows,indent=2)+'\n')
paths=[Path(__file__),source,inputs,reference/'report.json',reference/'samples.json',ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED',matched_reference_fields=matched,fatal_field=fatal,episode=episode,compile_command=cmd,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print('CAPTURED',matched,'fatal',fatal,episode,flush=True)
