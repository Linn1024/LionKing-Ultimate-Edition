"""Correct cursor logger field count before its first gameplay capture."""
from pathlib import Path
builder=Path(__file__).with_name('build_pride_menu197_observer.py')
cursor=Path(__file__).with_name('pride_menu208_cursor.inc')
def instrument209(s):
    anchor='static void FinalSceneBegin(CpuState *cpu,uint32_t pc) {'
    assert s.count(anchor)==1
    s=s.replace(anchor,'static void MenuCursor208(const char *,CpuState *);\n'+anchor)
    anchor='static void MenuObserve197(const char *kind,CpuState *cpu,uint32_t pc){'
    assert s.count(anchor)==1
    logger=cursor.read_text()
    wrong='"%s,%u,%u,%u,%u,%u,%u,%u,%u,%u\\n"'
    right='"%s,%u,%u,%u,%u,%u,%u,%u,%u\\n"'
    assert logger.count(wrong)==1
    logger=logger.replace(wrong,right)
    return s.replace(anchor,anchor+'MenuCursor208(kind,cpu);')+'\n'+logger
source=builder.read_text().replace('pride-menu197-observer','pride-menu209-observer').replace('snes_frame_counter<4000','snes_frame_counter<3000')
anchor="target = out / 'host.i'"
assert source.count(anchor)==1
source=source.replace(anchor,'s=instrument209(s)\n'+anchor)
source=source.replace('paths = [Path(__file__),bp,old,pre,target,rsp]',
                      'paths = [Path(__file__),builder,cursor,bp,old,pre,target,rsp]')
exec(compile(source,str(builder),'exec'))
