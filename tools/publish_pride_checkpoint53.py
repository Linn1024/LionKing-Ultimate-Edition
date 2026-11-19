"""Select the verified checkpoint development package in the public launcher."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-checkpoint-capability53';out=base/'publication';out.mkdir()
    source=base/'package-qualification/report.json';prior=bound(source);assert prior['result']=='PASS' and all(prior['checks'].values())
    packagepath=ROOT/'dist/installed-preview53/package-report.json';package=bound(packagepath)
    launcher=ROOT/'scripts/RunInstalledPreview.ps1'
    assert digest(launcher)==package['source_sha256'][launcher.relative_to(ROOT).as_posix()]
    candidate=base/'RunInstalledPreviewCandidate.ps1';text=candidate.read_text()
    anchor="$projectRoot = '"+str(ROOT)+"'";assert text.count(anchor)==1
    text=text.replace(anchor,'$projectRoot = Split-Path $PSScriptRoot -Parent')
    assert text==launcher.read_text().replace('dist/installed-preview50','dist/installed-preview53')
    manifest=ROOT/'game-data/install.json';helper=ROOT/'dist/PrepareSpriteAssets.exe';before=(digest(manifest),digest(helper))
    launcher.write_text(text)
    checks=dict(only_package_selection_changed=True,installed_data_and_helper_unchanged=before==(digest(manifest),digest(helper)),
                new_package_selected='dist/installed-preview53' in launcher.read_text())
    paths=[Path(__file__),source,packagepath,launcher,candidate,manifest,helper,ROOT/'build/pride-checkpoint-publish53-baseline/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,save_scope='current-build',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PUBLISHED',checks,flush=True)


if __name__=='__main__':main()
