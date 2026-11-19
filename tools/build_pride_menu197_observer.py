"""Read-only current139 native final-menu clock and callback observer."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound

base = ROOT / 'build/pride-hyena-entrance139'
bp = base / 'build-report.json'
b = bound(bp)
old = ROOT / 'build/pride-contact166-observer/build-report.json'
bound(old)
out = ROOT / 'build/pride-menu197-observer'
out.mkdir()
cwd = ROOT / 'build/pride-sprite-fresh44'
pre = old.parent / 'host-original.i'
s = pre.read_text()
declaration = 'static void MenuObserve197(const char *,CpuState *,uint32_t);\n'
anchor = 'static void FinalSceneBegin(CpuState *cpu,uint32_t pc) {'
assert s.count(anchor) == 1
s = s.replace(anchor, declaration + anchor)
for name in ('FinalSceneBegin', 'FinalInputHold', 'FinalInputDecision',
             'ContinueTransitionConfirm', 'ContinueTitleExit'):
    anchor = 'static void ' + name + '(CpuState *cpu,uint32_t pc) {'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + '\nMenuObserve197("' + name + '",cpu,pc);')
anchor = '_Bool __wrap_RtlRunFrame(uint32 inputs) {'
assert s.count(anchor) == 1
s = s.replace(anchor, 'static _Bool MenuPrevious197(uint32 inputs) {')
s += '''
static unsigned MenuWord197(unsigned at){return g_ram[at]|(unsigned)g_ram[at+1]<<8;}
static unsigned MenuPointer197(unsigned at){return MenuWord197(at)|(unsigned)g_ram[at+2]<<16;}
static void MenuObserve197(const char *kind,CpuState *cpu,uint32_t pc){
    const char *path=getenv("TLK_MENU197");
    if(!path || snes_frame_counter<4000)return;
    static FILE *file;
    if(!file){file=fopen(path,"w");if(!file)exit(119);fputs("kind,field,pc,scene,health,spares,credits,difficulty,brightness,choice,timer,padheld,padedge,action,entry,age,stack\\n",file);}
    fprintf(file,"%s,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\\n",kind,(unsigned)snes_frame_counter+(cpu?1:0),pc,
        MenuPointer197(0xdf),MenuWord197(0x2004),MenuWord197(0x1ffaa),MenuWord197(0x1ffa8),MenuWord197(0x1ff92),g_snes->ppu->inidisp,
        MenuWord197(0xa68e),MenuWord197(0xa6b4),MenuWord197(0x5a),MenuWord197(0x5c),MenuPointer197(0xb243),final_scene_entry,final_scene_age,cpu?cpu->S:0);
    fflush(file);
}
_Bool __wrap_RtlRunFrame(uint32 inputs){
    _Bool result=MenuPrevious197(inputs);MenuObserve197("frame",0,0);return result;
}
'''
target = out / 'host.i'
target.write_text(s)
cmd = b['compiles']['host'].copy()
original = Path(cmd[cmd.index('-o') + 1])
for flag, value in [('-c', target), ('-o', out/'host.obj'), ('-MT', out/'host.obj'), ('-MF', out/'host.d')]:
    cmd[cmd.index(flag)+1] = str(value)
with (out/'compile.log').open('wb') as f:
    subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs = argv('link '+(base/'link.rsp').read_text())[1:]
indices = [i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==original]
assert len(indices)==1
inputs[indices[0]] = (out/'host.obj').as_posix()
rsp = out/'link.rsp'
rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:
    subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked = {(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==323
paths = [Path(__file__),bp,old,pre,target,rsp]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,
    nonhost_inputs_unchanged=323,guest_writes_added=False,
    scope='Read-only pre-guard callbacks and native menu scalar fields. Needs current production neutrality qualification.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
