"""Extend ordinary first-revival input to observe later deaths without fixtures."""
import argparse
import json
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import environment
from verify_windows import hashes


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tail',choices=('neutral','right','oscillate'),default='right');args=p.parse_args()
    out=ROOT/'build/pride-repeated-route'/args.tail;out.mkdir(parents=True,exist_ok=True)
    base=ROOT/'build/pride-live-error-ui';binary=base/'error-ui-probe.exe';build=json.loads((base/'build-report.json').read_text())
    assert digest(binary)==build['runs']['probe']['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    original=ROOT/'build/pride-game-over-music/normal.tape';frames=8000
    words=[(256 if (i//240)%2==0 else 512) if args.tail=='oscillate' else 256 if args.tail=='right' else 0 for i in range(frames-2075)]
    tape=out/'ordinary.tape';tape.write_bytes(original.read_bytes()[:1669*2]+bytes((2075-1669)*2)+struct.pack('<'+'H'*len(words),*words))
    profile=ROOT/'build/pride-live-error-ui/audio-windows/native-aot/resources.ini'
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
        '--input',tape,'--frames',frames,'--ram-log',out/'route.ram','--wide','256','--wide-png',out/'picture.png']
    with (out/'run.log').open('wb') as log:
        run=subprocess.run(list(map(str,command)),cwd=ROOT,env=environment(out),stdout=log,stderr=subprocess.STDOUT,timeout=240)
    ram=[r.split() for r in (out/'route.ram').read_text().splitlines()];changes=[];previous=None
    for r in ram:
        key=(r[3],r[7])
        if key!=previous:changes.append(dict(field=int(r[0]),health=int(r[3],16),lives=int(r[7],16)));previous=key
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),base/'build-report.json',original,profile,ROOT/'tools/verify_pride_live_error_ui.py')}
    report=dict(result='OBSERVED',exit_code=run.returncode,changes=changes,guest=hashes(out/'run.log'),source_sha256=sources,
        binary_sha256=digest(binary),artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},
        loaded_states=False,guest_fixture_edits=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(run.returncode,changes,flush=True)


if __name__=='__main__':main()
