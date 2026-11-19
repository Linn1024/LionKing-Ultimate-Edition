"""Correct the actual preprocessed wrapper anchor; retain rejected211 attempt."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
builder=Path(__file__).with_name('build_pride_menu211_phases.py')
failed=ROOT/'build/pride-menu211-phases'
assert not (failed/'attempt-report.json').exists()
(failed/'attempt-report.json').write_text(json.dumps(dict(result='FAIL',stage='wrapper source anchor before compile',
    reason='Observer209 wrapper has no space before its opening brace.',
    source_sha256={builder.relative_to(ROOT).as_posix():digest(builder)}),indent=2)+'\n')
source=builder.read_text().replace('pride-menu211-phases','pride-menu212-phases')
source=source.replace("anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {'", "anchor='_Bool __wrap_RtlRunFrame(uint32 inputs){'")
source=source.replace('paths=[Path(__file__),bp,prior,pre,rsp]', 'paths=[Path(__file__),builder,bp,prior,pre,rsp]')
exec(compile(source,str(builder),'exec'))
