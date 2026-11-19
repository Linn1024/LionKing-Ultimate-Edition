"""Promote the qualified player/helper and upgrade the existing installation."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token47';out=base/'publication';out.mkdir()
    evidence=[base/name/'report.json' for name in ('launcher-verification','native75','allbugs-verification','artwork-verification','full-route/qualification','live-ui','guards')]
    for path in evidence:
        report=bound(path);assert report['result']=='PASS' and all(report['checks'].values()),path
    assets_path=ROOT/'build/pride-continue-token-assets/build-report.json';assets=bound(assets_path)
    baseline_path=ROOT/'build/pride-continue-token-publish-baseline/report.json';baseline=json.loads(baseline_path.read_text())
    for name in ('scripts/RunInstalledPreview.ps1','dist/PrepareSpriteAssets.exe','game-data/install.json'):
        row=baseline['historical_sources'][name];assert digest(ROOT/name)==digest(ROOT/row['archive'])==row['sha256'],name
    helper=ROOT/'dist/PrepareSpriteAssets.exe';staged=assets_path.parent/'tool/tlk_prepare_sprite_assets.exe'
    assert digest(staged)==assets['binary_sha256']
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';candidate=base/'RunInstalledPreviewCandidate.ps1'
    text=candidate.read_text();anchor="$projectRoot = 'C:\\TEMP2\\lionKing'";assert text.count(anchor)==1
    published_source=text.replace(anchor,'$projectRoot = Split-Path $PSScriptRoot -Parent')
    assert 'dist/installed-preview47' in published_source and 'required_sprite_policy_sha256' in published_source
    data=ROOT/'game-data';excluded={'install.json','setup-last.log'}
    protected={p.relative_to(ROOT).as_posix():digest(p) for directory in (ROOT/'settings',data) for p in directory.rglob('*') if p.is_file() and not (directory==data and p.name in excluded)}
    expected_path=assets_path.parent/'setup-verification/Game data & sprite assets/install.json'
    expected=json.loads(expected_path.read_text(encoding='utf-8-sig'))
    keys=('roms','scene_cache','menu_assets','native_final_assets','title_bank_assets','hud_assets','sprite_assets')
    cmd=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),
         '-SnesRom',str(ROOT/'Lion King, The (USA).sfc'),'-MdRom',str(ROOT/'Lion King, The (World).md'),'-NonInteractive']
    checks={};mutated=False
    try:
        shutil.copyfile(staged,helper);mutated=True
        with (out/'setup.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        actual=json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
        checks['actual_default_setup']=rc==0
        checks['existing_assets_settings_saves_preserved']=all(digest(ROOT/p)==sha for p,sha in protected.items())
        checks['tested_package_descriptors']=all(actual[k]==expected[k] for k in keys)
        checks['installed_files_match_manifest']=all(digest(data/actual[k]['file'])==actual[k]['sha256'] for k in keys if k!='roms')
        assert all(checks.values()),checks
        launcher.write_text(published_source)
        checks['published_launcher_equals_tested_candidate_except_root']=launcher.read_text().replace('$projectRoot = Split-Path $PSScriptRoot -Parent',anchor)==text
        checks['published_helper_exact']=digest(helper)==assets['binary_sha256']
        assert all(checks.values()),checks
    except BaseException:
        if mutated:
            for name in ('scripts/RunInstalledPreview.ps1','dist/PrepareSpriteAssets.exe','game-data/install.json','game-data/setup-last.log'):
                row=baseline['historical_sources'].get(name)
                if row:shutil.copyfile(ROOT/row['archive'],ROOT/name)
        raise
    paths=[Path(__file__),*evidence,assets_path,baseline_path,expected_path,candidate,launcher,helper,data/'install.json',ROOT/'scripts/Setup.ps1']
    report=dict(result='PASS',checks=checks,command=cmd,published=True,previous_package_preserved=True,
                preserved_files_sha256=protected,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PUBLISHED',sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
