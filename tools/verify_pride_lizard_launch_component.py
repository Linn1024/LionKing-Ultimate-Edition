"""Exercise launch constructor guards independently of the generated player."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-lizard-launch-work/component';out.mkdir()
    source=ROOT/'tools/test_pride_lizard_launch_audio.c'
    adapter=ROOT/'engine/runner/tlk_lizard_audio.c';binary=out/'component.exe'
    command=list(map(str,['C:/mingw32/bin/gcc.exe','-O2','-std=c11','-I',ROOT/'engine/runner',
        '-I',ROOT/'engine/snesrecomp/runner/src','-I',ROOT/'engine/snesrecomp/runner/src/snes',source,adapter,'-o',binary]))
    with (out/'compile.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    result=subprocess.run([str(binary)],cwd=ROOT,capture_output=True,check=True)
    (out/'run.log').write_bytes(result.stdout+result.stderr)
    paths=[Path(__file__),source,adapter,ROOT/'engine/runner/tlk_lizard_audio.h']
    report=dict(result='PASS',timer_cases=65536,original_dispatch_frames=3,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.decode().strip(),flush=True)


if __name__=='__main__':main()
