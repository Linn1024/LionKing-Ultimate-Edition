"""Read-only current139 Continue cursor observations with a plain C logger."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

failed=ROOT/'build/pride-menu207-observer'
assert not (failed/'attempt-report.json').exists()
failed_script=Path(__file__).with_name('build_pride_menu207_observer.py')
(failed/'attempt-report.json').write_text(json.dumps(dict(result='FAIL',stage='host compile',
    reason='Nested logging string replacement generated a literal newline in a C format string. No executable or capture produced.',
    source_sha256={failed_script.relative_to(ROOT).as_posix():digest(failed_script)},
    artifacts_sha256={p.name:digest(p) for p in failed.iterdir() if p.is_file()}),indent=2)+'\n')
builder=Path(__file__).with_name('build_pride_menu197_observer.py')
cursor=Path(__file__).with_name('pride_menu208_cursor.inc')
def instrument208(s):
    anchor='static void FinalSceneBegin(CpuState *cpu,uint32_t pc) {'
    assert s.count(anchor)==1
    s=s.replace(anchor,'static void MenuCursor208(const char *,CpuState *);\n'+anchor)
    anchor='static void MenuObserve197(const char *kind,CpuState *cpu,uint32_t pc){'
    assert s.count(anchor)==1
    return s.replace(anchor,anchor+'MenuCursor208(kind,cpu);')+'\n'+cursor.read_text()

source=builder.read_text().replace('pride-menu197-observer','pride-menu208-observer').replace('snes_frame_counter<4000','snes_frame_counter<3000')
anchor="target = out / 'host.i'"
assert source.count(anchor)==1
source=source.replace(anchor,'s=instrument208(s)\n'+anchor)
source=source.replace('paths = [Path(__file__),bp,old,pre,target,rsp]',
                      'paths = [Path(__file__),builder,cursor,bp,old,pre,target,rsp]')
exec(compile(source,str(builder),'exec'))
