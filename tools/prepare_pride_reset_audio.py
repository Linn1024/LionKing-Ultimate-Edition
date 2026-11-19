"""Prepare a reset-audio test installation with its pinned sound backend."""
import json
from pathlib import Path
import shutil

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound

base = ROOT/'build/pride-reset/audio-views'
build_path = base/'build-report.json'
build = bound(build_path)
out = ROOT/'build/pride-reset/audio-views2'
out.mkdir()
binary = base/'sdl-reset.exe'
assert digest(binary) == build['runs']['sdl']['binary_sha256']
backend = ROOT/'build/pride-raster-state/live/runtime/genesis_plus_gx_libretro.dll'
audit_path = ROOT/'build/pride-raster-state/live/owned-ui-save-audit/md-media/report.json'
audit = bound(audit_path)
assert audit['dll_sha256'] == digest(backend)
shutil.copy2(binary, out/binary.name)
shutil.copy2(backend, out/backend.name)
paths = [Path(__file__), build_path, audit_path, backend, out/backend.name]
report = dict(build)
report['source_sha256'] = {str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Prepared reset audio installation with verified backend',flush=True)
