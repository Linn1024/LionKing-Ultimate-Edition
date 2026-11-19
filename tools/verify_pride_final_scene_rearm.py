"""Test new-episode eligibility independently from the guest entry hook."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

def main():
    out=ROOT/'build/pride-final-scene-rearm-unit';out.mkdir()
    test=ROOT/'engine/tests/final_scene_lifecycle_test.c';scene=ROOT/'engine/runner/tlk_continue_scene.c'
    binary=out/'test.exe';cmd=['C:/mingw32/bin/gcc.exe','-O2','-I'+str(scene.parent),str(test),str(scene),'-o',str(binary)]
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    text=subprocess.check_output([str(binary)],text=True);assert '14 checks, 0 failures' in text
    (out/'run.log').write_text(text)
    paths=[Path(__file__),test,scene,scene.parent/'tlk_final_scene_lifecycle.h']
    result=dict(result='PASS',checks=14,command=cmd,log=text,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(text.strip(),flush=True)

if __name__=='__main__':main()
