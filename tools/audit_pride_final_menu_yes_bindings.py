"""Bind the confirmed-menu batch, including retained failed attempts, to its evidence."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-final-menu-yes-bindings';out.mkdir();checks={}
    reports=[
        'pride-final-menu-yes-original/report.json','pride-final-menu-yes-late-original/report.json',
        'pride-final-menu-yes-audit/report.json','pride-final-menu-yes-component/build-report.json',
        'pride-final-menu-yes-component/verification/report.json','pride-final-menu-yes-component/state-verification2/report.json',
        'pride-final-menu-player7/build-report.json','pride-final-menu-player7/yes/report.json',
        'pride-final-menu-player8/build-report.json','pride-final-menu-player8/yes/report.json',
        'pride-final-menu-player9/build-report.json','pride-final-menu-player9/yes/report.json',
        'pride-final-menu-player9/handoff/report.json','pride-final-menu-player9/handoff2/report.json',
        'pride-final-menu-player9/verification/report.json','pride-final-menu-player9/verification2/report.json',
        'pride-final-menu-player9/continue/report.json','pride-final-menu-player9/no/report.json',
        'pride-final-menu-player5/build-report.json','pride-final-menu-player5/continue/report.json',
        'pride-final-menu-player5/verification/report.json','pride-final-menu-player5/no/report.json',
        'pride-final-menu-player2/continue/report.json',
        'pride-final-menu-scene/build-report.json','pride-final-menu-scene/verification/report.json',
        'pride-final-art-installed/verification4/report.json','pride-final-art-setup/build-report.json',
        'pride-final-art-setup/verification/report.json',
        'pride-cold-boot2/launcher-verification/report.json']
    for name in reports:
        path=ROOT/'build'/name;bound(path);checks[name+'_bound']=True
    for name in ('pride-final-menu-player7','pride-final-menu-player8','pride-final-menu-player9'):
        folder=ROOT/'build'/name;report=json.loads((folder/'build-report.json').read_text())
        checks[name+'_binary']=digest(folder/'player.exe')==report['binary_sha256']
        checks[name+'_all_link_inputs']=all(digest(ROOT/p)==sha for p,sha in report['link_inputs_sha256'].items())
    component=ROOT/'build/pride-final-menu-yes-component'
    checks['scene_reader_binary']=digest(component/'reader2.dll')==json.loads((component/'verification/report.json').read_text())['binary_sha256']
    checks['state_reader_binary']=digest(component/'state.dll')==json.loads((component/'state-verification2/report.json').read_text())['binary_sha256']
    checks['retained_failure_honest']=json.loads((ROOT/'build/pride-final-menu-player7/yes/report.json').read_text())['result']=='FAIL'
    manifest=ROOT/'build/pride-final-menu-scene/installed/install.json';info=json.loads(manifest.read_text())
    package=manifest.parent/info['menu_assets']['file'];raw=package.read_bytes()
    checks['actual_setup_package']=len(raw)==113500 and int.from_bytes(raw[8:12],'little')==2 and digest(package)==info['menu_assets']['sha256']
    helper=json.loads((ROOT/'build/pride-final-menu-scene/build-report.json').read_text())
    checks['published_helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')==helper['published_helper_sha256']
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    launcher=json.loads((ROOT/'build/pride-cold-boot2/launcher-verification/report.json').read_text())
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')==launcher['source_sha256']['Play Standalone Preview.cmd']
    paths=[Path(__file__),manifest,package,*[ROOT/'build'/name for name in reports]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
