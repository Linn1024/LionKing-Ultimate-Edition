"""Current corrected real-stack guards and source-change restart policy."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride-hyena-probe103-component';out.mkdir()
test=ROOT/'engine/tests/hyena_walking_probe_test.c';module=ROOT/'engine/runner/tlk_hyena_probe.c'
command=['C:/mingw32/bin/gcc.exe','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(ROOT/'engine/snesrecomp/runner/src'),str(test),str(module),'-o',str(out/'test.exe')]
subprocess.run(command,check=True);r=subprocess.run([str(out/'test.exe')],capture_output=True,text=True)
checks=dict(exit=r.returncode==0,guard_and_source_checks4309=r.stdout.strip()=='PASS 4309 checks')
paths=[Path(__file__),test,module,ROOT/'engine/runner/tlk_hyena_probe.h',out/'test.exe']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=command,output=r.stdout,stderr=r.stderr,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(r.stdout,checks,flush=True)
