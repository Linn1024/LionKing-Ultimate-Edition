"""Include the original first tail frame and write only reviewed address metadata."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
template=Path(__file__).with_name('audit_cant_wait470_tail.py')
s=template.read_text().replace('build/cant-wait470-tail','build/cant-wait471-tail').replace('range(0x3ce90,0x3d1c0)','range(0x3ce80,0x3d1c0)').replace('assert len(pairs)>=8','assert len(pairs)==11')
exec(compile(s,str(template),'exec'))
report=ROOT/'build/cant-wait471-tail/report.json';r=json.loads(report.read_text())
header=ROOT/'engine/runner/tlk_cw_tail_metadata.h';header.write_text('/* Exact shared original rhino tail poses, including native RAM-backed frames.\n * Address metadata only; native pixels and timing remain unchanged. */\nstatic const unsigned cw_tail_poses[]={'+','.join(p['native_pose'] for p in r['pairs'])+'};\nstatic const unsigned cw_tail_descriptors[]={0xc58c08};\n')
(report.parent/'metadata.json').write_text(json.dumps(dict(result='VERIFIED_METADATA',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),template,report,header)}),indent=2)+'\n')
