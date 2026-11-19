"""Select the qualified installed development package; preserve frozen launcher bytes."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-music-output65';bp=base/'build-report.json';build=bound(bp)
    proofs=[base/name/'report.json' for name in ('component','completion','lifecycle','audio-device','windows-visible','package-play2','native75','allbugs-verification')]
    for path in proofs:
        report=bound(path);assert report['result']=='PASS' and all(report.get('checks',{'component':True}).values()),path
    packagepath=ROOT/'dist/installed-preview65/package-report.json';package=bound(packagepath)
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';history=ROOT/'tools/pride_arena_history.py'
    assert digest(launcher)==package['source_sha256'][launcher.relative_to(ROOT).as_posix()]
    candidate=base/'RunInstalledPreviewCandidate.ps1';text=candidate.read_text()
    fixed="$projectRoot = '"+str(ROOT)+"'";assert text.count(fixed)==1
    text=text.replace(fixed,'$projectRoot = Split-Path $PSScriptRoot -Parent')
    assert text==launcher.read_text().replace('dist/installed-preview53','dist/installed-preview65')
    assert digest(ROOT/'dist/installed-preview65/LionKing.exe')==build['binary_sha256']
    manifest=ROOT/'game-data/install.json';helper=ROOT/'dist/PrepareSpriteAssets.exe';protected=(digest(manifest),digest(helper))
    archive=ROOT/'build/pride-music-publish65-baseline';assert not archive.exists()
    out=base/'publication';assert not out.exists();archive.mkdir();items={}
    names=['scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-music-output.md','docs/pride-lands-status.md','engine/docs/devlog.md','README.md',
           'engine/runner/tlk_native_audio_owner.c','engine/runner/tlk_native_audio_owner.h','engine/runner/tlk_audio.c','engine/runner/tlk_audio.h']
    for name in names:
        path=ROOT/name;target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        items[name]=dict(sha256=digest(path),archive=target.relative_to(ROOT).as_posix())
    (archive/'report.json').write_text(json.dumps(dict(historical_sources=items),indent=2)+'\n')
    anchor="    folders.append('pride-music-output64-baseline')";h=history.read_text();assert h.count(anchor)==1
    history.write_text(h.replace(anchor,anchor+"\n    folders.append('pride-music-publish65-baseline')"))
    launcher.write_text(text);out.mkdir()
    checks=dict(only_launcher_package_selection_changed=True,installed_data_and_helper_unchanged=protected==(digest(manifest),digest(helper)),
                package65_selected='dist/installed-preview65' in launcher.read_text())
    paths=[Path(__file__),bp,*proofs,packagepath,launcher,history,candidate,manifest,helper,archive/'report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,current_build_saves_only=True,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PUBLISHED',build['binary_sha256'],checks,flush=True)


if __name__=='__main__':main()
