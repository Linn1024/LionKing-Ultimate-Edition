"""Current native phase observer, explicit stdin language before the input."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
builder=Path(__file__).with_name('build_pride_menu211_phases.py')
failed=ROOT/'build/pride-menu212-phases'
assert not (failed/'attempt-report.json').exists()
script=Path(__file__).with_name('build_pride_menu212_phases.py')
(failed/'attempt-report.json').write_text(json.dumps(dict(result='FAIL',stage='compiler argument ordering',
    reason='GCC language option must precede stdin input.',
    source_sha256={script.relative_to(ROOT).as_posix():digest(script)},
    artifacts_sha256={p.name:digest(p) for p in failed.iterdir() if p.is_file()}),indent=2)+'\n')
source=builder.read_text().replace('pride-menu211-phases','pride-menu213-phases')
source=source.replace("anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {'", "anchor='_Bool __wrap_RtlRunFrame(uint32 inputs){'")
source=source.replace("cmd+=['-x','cpp-output']", "cmd[cmd.index('-c'):cmd.index('-c')]=['-x','cpp-output']")
source=source.replace('paths=[Path(__file__),bp,prior,pre,rsp]', 'paths=[Path(__file__),builder,bp,prior,pre,rsp]')
exec(compile(source,str(builder),'exec'))
