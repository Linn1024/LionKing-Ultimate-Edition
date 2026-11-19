"""Compare the production guard to the independently decoded original tag oracle."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_ledge_history import bound


def main():
    oracle_path=ROOT/'build/pride-ledge-tags/report.json';oracle=bound(oracle_path)
    assert oracle['result']=='ORIGINAL_LEDGE_TAG_BRANCHES_MATCH'
    out=ROOT/'build/pride-ledge-work/component';out.mkdir()
    tags=oracle['directions']['left']['accepted_tags']
    assert tags==oracle['directions']['right']['accepted_tags']
    table=out/'original-tags.bin';expected=bytearray(65536)
    for tag in tags:expected[tag]=1
    table.write_bytes(expected)
    binary=out/'component.exe';source=ROOT/'tools/test_pride_ledge_audio.c';adapter=ROOT/'engine/runner/tlk_ledge_audio.c'
    command=list(map(str,['C:/mingw32/bin/gcc.exe','-O2','-std=c11','-I',ROOT/'engine/runner',
        '-I',ROOT/'engine/snesrecomp/runner/src','-I',ROOT/'engine/snesrecomp/runner/src/snes',source,adapter,'-o',binary]))
    with (out/'compile.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    result=subprocess.run([str(binary),str(table)],cwd=ROOT,capture_output=True,check=True)
    (out/'run.log').write_bytes(result.stdout+result.stderr)
    paths=[Path(__file__),source,adapter,ROOT/'engine/runner/tlk_ledge_audio.h',oracle_path]
    report=dict(result='PASS',original_byte_tag_branch_comparisons=512,production_word_tag_cases_per_direction=65536,
        positive_original_tags=tags,guest_and_cpu_writes_added=False,original_dispatch_frames=3,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.decode().strip(),flush=True)


if __name__=='__main__':main()
