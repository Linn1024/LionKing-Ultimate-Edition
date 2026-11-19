"""Seal failed low-space harness attempts and lossless archive provenance."""
import gzip
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
def record(folder,script,scope,extra=None):
    out=ROOT/'build'/folder;dest=out/'attempt-report.json';assert not dest.exists()
    paths=[Path(__file__),ROOT/'tools'/script,ROOT/'build/pride-menu226-integrated/build-report.json']
    data=dict(result='FAIL',scope=scope,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    if extra:data.update(extra)
    dest.write_text(json.dumps(data,indent=2)+'\n');print('RETAINED',folder,flush=True)
out=ROOT/'build/pride-menu232-resource-ui';sha=hashlib.sha256();count=0;size=0;last=None
with gzip.open(out/'tree.jsonl.gz','rb') as f:
    for line in f:
        sha.update(line);size+=len(line);last=json.loads(line);count+=1
(out/'trace-metadata.json').write_text(json.dumps(dict(rows=count,uncompressed_bytes=size,uncompressed_sha256=sha.hexdigest()),indent=2)+'\n')
record('pride-menu232-resource-ui','verify_pride_menu232_resource_ui.py',
    'Removing --frames alone still leaves input replay noninteractive. No power-on restart checkpoint; source persisted but restart unqualified. Corrected owncurrent cold-load234 passes. No game implementation failure inferred.',
    dict(last=dict(field=last['field'],modal=last['modal'],help=last['help'])))
record('pride-menu226-integrated/allbugs-verification','verify_pride_menu239_allbugs.py',
    'Space guard failed before either pilot/player launch. No All Bugs comparison ran. Diagnostic executable238 subsequently losslessly archived; restore after freeing space. Use fresh output for corrected run.')
record('pride-menu240-md-timing','verify_pride_menu240_md_timing.py',
    'G output root creation failed with WinError2 before control/player launch. Free-space counter did not prove destination was usable. No mixed-timing proof.')
control=ROOT/'build/pride-menu241-md-timing-local/control';archive=json.loads((control/'audio-archive.json').read_text())
sha=hashlib.sha256()
with gzip.open(control/archive['archive'],'rb') as f:
    for data in iter(lambda:f.read(1024*1024),b''):sha.update(data)
assert sha.hexdigest()==archive['original_sha256']
record('pride-menu241-md-timing-local','verify_pride_menu241_md_timing_local.py',
    'Control process observed exit0. Selected run hit disk full saving first ready screenshot; zero-byte PNG and partial audio remain. No passing guest/audio/pixel comparison. Complete control WAV losslessly archived after failure.',
    dict(control_exit_observed=0,control_wave_lossless_archive_verified=True,selected_capture_complete=False))
