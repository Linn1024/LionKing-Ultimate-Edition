"""Bind installed-native-payload evidence and verify preparation-only startup."""
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-final-native-bindings';out.mkdir();checks={}
    names=['pride-final-native-installed/build-report.json','pride-final-native-installed/verification/report.json',
        'pride-final-native-installed/setup-verification/report.json','pride-final-native-installed/window/report.json',
        'pride-final-native-player11/build-report.json','pride-final-native-player11/verification/report.json',
        'pride-final-native-player11/verification2/report.json','pride-final-native-player11/game-over/report.json',
        'pride-final-menu-player10/build-report.json','pride-final-menu-player10/layout/report.json',
        'pride-final-menu-player10/handoff/report.json','pride-final-menu-player10/verification2/report.json',
        'pride-final-menu-layout-bindings/report.json','pride-final-menu-yes-bindings/report.json',
        'pride-final-art-setup/verification/report.json','pride-final-menu-scene/build-report.json']
    for name in names:bound(ROOT/'build'/name);checks[name+'_bound']=True
    base=ROOT/'build/pride-final-native-installed';build=json.loads((base/'build-report.json').read_text())
    checks['published_helper_matches_build']=digest(ROOT/'dist/PrepareFinalAssets.exe')==build['published_helper_sha256']==digest(base/'cmake/tlk_prepare_final_assets.exe')
    reader=base/'reader.dll';checks['reader_matches_verified_binary']=digest(reader)==json.loads((base/'verification/report.json').read_text())['binary_sha256']
    symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(reader)],text=True)
    checks['reader_no_rom_decoder']='TlkMdDecompress' not in symbols and 'TlkFinalNativePrepare' not in symbols
    player=ROOT/'build/pride-final-native-player11';report=json.loads((player/'build-report.json').read_text())
    checks['player_binary']=digest(player/'player.exe')==report['binary_sha256']
    checks['all315_link_inputs']=len(report['link_inputs_sha256'])==315 and all(digest(ROOT/p)==sha for p,sha in report['link_inputs_sha256'].items())
    manifest=base/'actual install/install.json';info=json.loads(manifest.read_text())
    checks['actual_installed_native']=digest(manifest.parent/info['native_final_assets']['file'])==info['native_final_assets']['sha256']==digest(base/'native.assets')
    checks['actual_installed_md_menu_unchanged']=digest(manifest.parent/info['menu_assets']['file'])=='f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    checks['old_helper_archived']=digest(ROOT/'build/pride-final-native-installed-baseline/dist/PrepareFinalAssets.exe')=='8ad57086b2269e4ab72632f3c5d1f30cddc1a2e4ee0480a650161fa8fd8f354b'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    status=subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine',text=True)
    checks['framework_submodules_unmodified']=not status.strip()
    # Preparation mode is intentionally permitted before runtime packages exist.
    cmd=[str(player/'player.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),
        '--config',str(out/'host.ini'),'--resource-profile',str(out/'unused.ini'),'--prepare-resources',str(out/'scenes.cache'),'--no-audio']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    with (out/'prepare.log').open('wb') as log:result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    checks['preparation_only_needs_no_runtime_packages']=result.returncode==0 and b'resource_cache=prepared' in (out/'prepare.log').read_bytes()
    checks['preparation_only_cache_matches_setup']=digest(out/'scenes.cache')==info['scene_cache']['sha256']
    checks['retained_failed_assumption_honest']=json.loads((player/'verification/report.json').read_text())['result']=='FAIL'
    paths=[Path(__file__),manifest,*[ROOT/'build'/name for name in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,preparation_command=cmd,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
