"""Bind original-flight corpus and negative semantic-owner predicate checks."""
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    out=ROOT/'build/pride-flight-player/role-verification';out.mkdir()
    corpus=ROOT/'build/native-pickup-flight2/report.json';r=bound(corpus)
    assert r['fixed_active_flight_samples']==24
    source=ROOT/'tools/test_pride_pickup_flight_role.c';header=ROOT/'engine/runner/tlk_pickup_flight_role.h'
    exe=out/'check.exe'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-std=c11',str(source),'-o',str(exe)],check=True,cwd=ROOT)
    completed=subprocess.run([str(exe),str(ROOT/'build/native-pickup-flight')],check=True,capture_output=True,text=True,cwd=ROOT)
    (out/'run.log').write_text(completed.stdout+completed.stderr)
    matches=re.search(r'PASS (\d+) checks, (\d+) original fixed-flight snapshots',completed.stdout)
    assert matches and matches.groups()==('9980','24')
    paths=[Path(__file__),source,header,corpus,exe,out/'run.log']
    report=dict(result='PASS',original_flight_snapshots=24,semantic_predicate_checks=480,total_corpus_and_predicate_checks=9980,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(completed.stdout.strip(),flush=True)


if __name__=='__main__':main()
