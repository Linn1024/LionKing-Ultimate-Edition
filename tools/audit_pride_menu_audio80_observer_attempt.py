"""Retain the failed observer's inherited-host lookup and completed compile files."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    folder=ROOT/'build/pride-menu-audio80/allbugs-observer';report=folder/'attempt-report.json'
    assert not report.exists() and (folder/'host.obj').exists() and not (folder/'player.exe').exists()
    source=ROOT/'tools/build_pride_menu_audio80_observer.py';base=ROOT/'build/pride-menu-audio80/build-report.json'
    data=json.loads(base.read_text());host=data['compiles']['host'];actual=host[host.index('-o')+1]
    paths=[Path(__file__),source,ROOT/'tools/build_pride_checkpoint52_allbugs.py',base]
    result=dict(result='FAILED_INHERITED_HOST_LOOKUP',reason='Original observer builder expected candidate80/host.obj, but the two-object relink inherits public74/host.obj. Host preprocessing and compilation completed; assertion rejected the link input lookup. No player was linked or run.',
                actual_host_object=actual,corrected_builder='tools/build_pride_menu_audio80_observer2.py',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()})
    report.write_text(json.dumps(result,indent=2)+'\n');print(result['result'])


if __name__=='__main__':main()
