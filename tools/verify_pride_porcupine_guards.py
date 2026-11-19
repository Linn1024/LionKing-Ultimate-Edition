"""Run semantic-owner rejection tests against the production runtime module."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-porcupine-runtime-guards';out.mkdir()
    runtime=ROOT/'engine/runner/tlk_porcupine_attack_runtime.c'
    model=ROOT/'engine/runner/tlk_porcupine_attack.c'
    test=ROOT/'tools/test_pride_porcupine_guards.c'
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-I'+str(ROOT/'engine/runner'),
         '-I'+str(ROOT/'engine/snesrecomp/runner/src'),str(test),str(runtime),str(model),'-o',str(out/'guards.exe')]
    subprocess.run(cmd,cwd=ROOT,check=True)
    run=subprocess.run([str(out/'guards.exe')],cwd=ROOT,capture_output=True,text=True,check=True)
    (out/'run.log').write_text(run.stdout+run.stderr)
    paths=[Path(__file__),test,runtime,model,runtime.with_suffix('.h'),model.with_suffix('.h')]
    report=dict(result='PASS' if run.stdout.strip()=='PASS 51' else 'FAIL',checks=51,compile_command=cmd,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],run.stdout.strip(),flush=True)


if __name__=='__main__':main()
