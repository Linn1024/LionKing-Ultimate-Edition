"""Read-only current139 Continue cursor observations, separate from clock CSV."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
failed=ROOT/'build/pride-menu206-observer'
attempt=failed/'attempt-report.json'
assert not attempt.exists()
script=Path(__file__).with_name('build_pride_menu206_observer.py')
(failed/'source.py').write_bytes(script.read_bytes())
attempt.write_text(json.dumps(dict(result='FAIL',stage='CSV source-anchor assertion before compile',
    reason='Overcomplicated newline/format anchor; no executable or captures produced.',
    source_sha256={script.relative_to(ROOT).as_posix():digest(script)},
    artifacts_sha256={'source.py':digest(failed/'source.py')}),indent=2)+'\n')
builder=Path(__file__).with_name('build_pride_menu197_observer.py')
source=builder.read_text().replace('pride-menu197-observer','pride-menu207-observer').replace('snes_frame_counter<4000','snes_frame_counter<3000')
anchor="target = out / 'host.i'"
assert source.count(anchor)==1
extra=r'''
anchor207='static void FinalSceneBegin(CpuState *cpu,uint32_t pc) {'
assert s.count(anchor207)==1
s=s.replace(anchor207,'static void MenuCursor207(const char *,CpuState *);\n'+anchor207)
anchor207='static void MenuObserve197(const char *kind,CpuState *cpu,uint32_t pc){'
assert s.count(anchor207)==1
s=s.replace(anchor207,anchor207+'MenuCursor207(kind,cpu);')
s += r"""
static void MenuCursor207(const char *kind,CpuState *cpu){
    const char *path=getenv("TLK_MENU_CURSOR207");
    if(!path || snes_frame_counter<3000)return;
    static FILE *file;
    if(!file){file=fopen(path,"w");if(!file)exit(121);fputs("kind,field,scene,credits,cursor,x,action,pose,timer\\n",file);}
    unsigned at=MenuWord197(0xa68e),valid=at>0x1000 && at<0xff80;
    fprintf(file,"%s,%u,%u,%u,%u,%u,%u,%u,%u\\n",kind,(unsigned)snes_frame_counter+(cpu?1:0),MenuPointer197(0xdf),MenuWord197(0x1ffa8),at,
        valid?MenuWord197(at+8):0,valid?MenuPointer197(at+0x30):0,valid?MenuWord197(at+0x12):0,MenuWord197(0xa6b4));
    fflush(file);
}
"""
# These appended C strings require one backslash in the generated source.
s=s.replace('timer\\n"','timer\n"').replace('%u\\n",kind','%u\n",kind')
'''
source=source.replace(anchor,extra+'\n'+anchor)
source=source.replace('paths = [Path(__file__),bp,old,pre,target,rsp]',
                      'paths = [Path(__file__),builder,bp,old,pre,target,rsp]')
exec(compile(source,str(builder),'exec'))
