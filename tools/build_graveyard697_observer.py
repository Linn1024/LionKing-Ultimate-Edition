"""Private read-only whole-level actor/pose observer; maintained runtime remains untouched."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard684/build-report.json';b=bound(reference);base=reference.parent
out=ROOT/'build/graveyard697-observer';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
shutil.copytree(ROOT/'engine/runner',out/'runner',dirs_exist_ok=True)
p=out/'runner/tlk_wide.c';s=p.read_text()
s=s.replace('static uint32_t logged[8192];static unsigned logged_count;', 'static uint64_t logged[8192];static unsigned logged_count;')
s=s.replace('frame,object,position,pose,flags,palette,colors\\n','frame,object,position,pose,flags,palette,descriptor,action,actor_x,actor_y,mapped_role,colors\\n')
s=s.replace('if (pose_trace && rd16(g_ram+0x1ff9e)==0 && (rd16(g_ram+0xdf)==0x387 || rd16(g_ram+0xdf)==0x80d)) {','if (pose_trace && rd16(g_ram+0x1ff9e)==2 && rd24(g_ram+0xdf)==0xc003eb) {')
s=s.replace('uint32_t key=piece->pose | palette<<24;unsigned n=0;', 'unsigned position=obj<=0xfffa?rd16(g_ram+(unsigned)obj+4):0; unsigned actor=position>=0x8008 && position<=0xff88?position-8:0; unsigned descriptor=actor?rd24(g_ram+actor+4):0; uint64_t key=((uint64_t)descriptor<<32)|piece->pose|palette<<24;unsigned n=0;')
s=s.replace('fprintf(pose_trace,"\\n");fflush(pose_trace);','fprintf(pose_trace,"\\n");fflush(pose_trace);')
anchor='for (unsigned c=0;c<16;c++) fprintf(pose_trace,"%04x",g_ppu->cgram[128+palette*16+c]);'
s=s.replace(anchor,'fprintf(pose_trace,"%06x,%06x,%u,%u,%u,",descriptor,actor?rd24(g_ram+actor+0x30):0,actor?rd16(g_ram+actor+8):0,actor?rd16(g_ram+actor+10):0,TlkMdSpritesDrawRole(piece->pose,palette));\n            '+anchor)
assert s!=p.read_text();p.write_text(s)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];cmd=b['compiles']['wide'].copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/'wide.obj'
for flag,value in (('-o',obj),('-MT',obj),('-MF',out/'wide.d'),('-c',out/'runner/pride/final/pride_final_wide.c')):cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
indices=[i for i,x in enumerate(inputs) if not x.startswith('-') and (cwd/x).resolve()==old];assert len(indices)==1;inputs[indices[0]]=obj.as_posix()
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
paths=[Path(__file__),reference,ROOT/'engine/runner/tlk_wide.c',p]
(out/'report.json').write_text(json.dumps(dict(result='BUILT',scope=__doc__,binary_sha256=digest(out/'player.exe'),compile=cmd,source_sha256={x.relative_to(ROOT).as_posix():digest(x) for x in paths}),indent=2)+'\n');print('BUILT',flush=True)
