"""Real callback/controller source guards, all action counters and narrow mute."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-lizard-voice74-component';out.mkdir()
    paths=[ROOT/'engine/tests/lizard_voice_entry_test.c',ROOT/'engine/runner/tlk_lizard_audio.c',ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/snesrecomp/runner/src/sha256.c']
    cmd=['C:/mingw32/bin/gcc.exe','-O2','-ffunction-sections','-fdata-sections','-DTLK_LIZARD_VOICE_TIMING_AVAILABLE=1']
    for p in ('engine/runner','engine/snesrecomp/runner/src','engine/snesrecomp/runner/src/snes'):cmd+=['-I'+str(ROOT/p)]
    cmd+=list(map(str,paths))+['-Wl,--gc-sections','-lm','-o',str(out/'test.exe')]
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    run=subprocess.run([str(out/'test.exe')],cwd=out,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,check=True);(out/'run.log').write_text(run.stdout)
    paths+=[Path(__file__),ROOT/'engine/runner/tlk_lizard_audio.h',ROOT/'engine/runner/tlk_lizard_voice_policy.h',ROOT/'engine/runner/tlk_audio.h']
    report=dict(result='PASS' if 'PASS ' in run.stdout else 'FAIL',command=cmd,output=run.stdout,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(run.stdout,flush=True)


if __name__=='__main__':main()
