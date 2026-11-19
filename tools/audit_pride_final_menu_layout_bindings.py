"""Bind viewport-layout evidence and retained predecessor reports to actual files."""
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-final-menu-layout-bindings';out.mkdir();checks={}
    names=['pride-final-menu-layout-evidence/report.json',
        'pride-final-menu-layout-component/build-report.json','pride-final-menu-layout-component/verification/report.json',
        'pride-final-menu-player10/build-report.json','pride-final-menu-player10/layout/report.json',
        'pride-final-menu-player10/verification2/report.json','pride-final-menu-player10/handoff/report.json',
        'pride-final-menu-player9/build-report.json','pride-final-menu-player9/yes/report.json',
        'pride-final-menu-player9/continue/report.json','pride-final-menu-player9/no/report.json',
        'pride-final-menu-player9/handoff2/report.json','pride-final-menu-yes-component/verification/report.json',
        'pride-final-menu-yes-component/state-verification2/report.json','pride-final-menu-yes-bindings/report.json',
        'pride-final-menu-scene/build-report.json']
    for name in names:bound(ROOT/'build'/name);checks[name+'_bound']=True
    base=ROOT/'build/pride-final-menu-player10';build=json.loads((base/'build-report.json').read_text())
    checks['player_binary']=digest(base/'player.exe')==build['binary_sha256']
    checks['all314_link_inputs']=len(build['link_inputs_sha256'])==314 and all(digest(ROOT/name)==sha for name,sha in build['link_inputs_sha256'].items())
    component=ROOT/'build/pride-final-menu-layout-component';test=json.loads((component/'verification/report.json').read_text())
    checks['reader_binary']=digest(component/'reader.dll')==test['binary_sha256']
    symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(component/'reader.dll')],text=True)
    checks['reader_has_no_rom_decoder']='TlkMdDecompress' not in symbols and 'TlkFinalArtPrepare' not in symbols
    manifest=ROOT/'build/pride-final-menu-scene/installed/install.json';info=json.loads(manifest.read_text())
    package=manifest.parent/info['menu_assets']['file']
    checks['installed_package_unchanged']=digest(package)==info['menu_assets']['sha256']=='f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    checks['published_helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='8ad57086b2269e4ab72632f3c5d1f30cddc1a2e4ee0480a650161fa8fd8f354b'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    # Keep the reviewed current launcher identity, independently of old baselines.
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    status=subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine',text=True)
    checks['framework_submodules_unmodified']=not status.strip()
    paths=[Path(__file__),manifest,package,*[ROOT/'build'/name for name in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
