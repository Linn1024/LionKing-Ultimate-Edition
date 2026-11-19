"""Generate an isolated original-clear forwarding seam from copied config."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-rng-player';out.mkdir();cfg=out/'recomp';shutil.copytree(ROOT/'engine/recomp',cfg)
    path=cfg/'bankc0.cfg';text=path.read_text();assert 'hle_func 7958' not in text
    path.write_text(text+'\n# Original clear body with the independent scene-entry RNG seam.\nhle_func 7958 TlkRngEntryDispatch\n')
    backend=ROOT/'engine/build/snesrecomp-codegen';generated=out/'generated'
    cmd=[sys.executable,backend/'tools/v2_emit.py','--rom',ROOT/'Lion King, The (USA).sfc','--cfg-dir',cfg,'--out-dir',generated,
         '--no-host-root-scan','--cfg-roots','--analysis-backend','native','--max-insns',4096,'--max-nodes',100000,
         '--bank-shard-threshold-kib',4096,'--bank-shard-pc-span','0x800']
    with (out/'generation.log').open('wb') as log:subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    unit=generated/'bankc0_part1f_v2.c';assert 'TlkRngEntryDispatch(cpu)' in unit.read_text()
    report=dict(result='GENERATED',command=list(map(str,cmd)),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),*sorted((ROOT/'engine/recomp').glob('*.cfg'))]},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in [path,unit,out/'generation.log']},canonical_configuration_modified=False)
    (out/'generation-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Original clear forwarding seam generated in isolation',flush=True)


if __name__=='__main__':main()
