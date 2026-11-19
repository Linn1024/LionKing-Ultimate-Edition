"""Archive exact smoke-test settings so later user customization stays independent."""
import json
from pathlib import Path
import shutil

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-launch2';raw_path=base/'launcher-smoke/report.json';raw=json.loads(raw_path.read_text());assert raw['result']=='PASS' and all(raw['checks'].values())
    out=base/'launcher-inputs';out.mkdir();sources={};mapping={}
    for name,sha in raw['source_sha256'].items():
        path=ROOT/name;assert digest(path)==sha,name
        if name.startswith('settings/development-preview/'):
            captured=out/path.name;shutil.copy2(path,captured);assert digest(captured)==sha
            mapping[name]=captured.relative_to(ROOT).as_posix();sources[captured.relative_to(ROOT).as_posix()]=sha
        else:sources[name]=sha
    for name,sha in raw['artifacts_sha256'].items():assert digest(raw_path.parent/name)==sha,name
    boot=ROOT/'settings/development-preview/tlk_practice_boot.state';shutil.copy2(boot,out/boot.name)
    data=(out/boot.name).read_bytes();assert data[:8]==b'TLKSTAT1' and int.from_bytes(data[12:16],'little')==0
    for path in (Path(__file__),raw_path,out/boot.name):sources[path.relative_to(ROOT).as_posix()]=digest(path)
    report=dict(result='PASS',checks=dict(actual_launcher_smoke_passed=True,exact_input_bytes_archived=True,actual_native_boot_archived=True),captured_source_paths=mapping,
                source_sha256=sources,experimental_preview=True,default_installed_player_replaced=False)
    (base/'launcher-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS preview settings snapshot',flush=True)


if __name__=='__main__':main()
