"""Publish output-only menu audio only after complete current regression gates."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    raise RuntimeError('Build83 is superseded by the verified Options effects-enable correction; do not publish it.')
    base=ROOT/'build/pride-menu-output83';bp=base/'build-report.json';build=bound(bp)
    proofs=[base/name/'report.json' for name in ('route','resume','windows-ui','regression','native75','allbugs-verification','package-play')]
    proofs += [ROOT/'build'/name/'report.json' for name in ('pride-menu-output83-owner-component','pride-menu-output83-controller','pride-menu-output84-isolation','pride-menu-audio80-originals')]
    for path in proofs:
        r=bound(path);assert r['result'] in ('PASS','MENU_CUE_MEANINGS_VERIFIED') and all(r.get('checks',{'pass':True}).values()),path
    assert build['current_owner_schema']==3 and build['unchanged_candidate80_inputs']==319 and len(build['link_inputs_sha256'])==322
    assert all(digest(ROOT/name)==sha for name,sha in build['link_inputs_sha256'].items())
    for label in ('audio','resources','owner'):assert '-DTLK_NATIVE_AUDIO_OWNER_AVAILABLE=1' in build['compiles'][label]
    assert not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    packagepath=ROOT/'dist/installed-preview83/package-report.json';bound(packagepath)
    assert digest(ROOT/'dist/installed-preview83/LionKing.exe')==build['binary_sha256']
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';history=ROOT/'tools/pride_arena_history.py';candidate=base/'RunInstalledPreviewCandidate.ps1'
    before=launcher.read_text();assert before.count('dist/installed-preview74')==1
    after=before.replace('dist/installed-preview74','dist/installed-preview83')
    fixed="$projectRoot = '"+str(ROOT)+"'";assert candidate.read_text()==after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',fixed)
    protected_paths=[ROOT/'game-data/install.json',ROOT/'dist/PrepareSpriteAssets.exe',ROOT/'dist/installed-preview74/LionKing.exe']
    protected={p.relative_to(ROOT).as_posix():digest(p) for p in protected_paths}
    archive=ROOT/'build/pride-menu-publish83-baseline';archive.mkdir();rows={}
    names=['scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-menu-audio.md','docs/pride-audio-dispatch.md','docs/launchers.md','README.md','engine/docs/devlog.md']
    for name in names:
        p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
    (archive/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
    anchor="    folders.append('pride-menu-output83-baseline')";text=history.read_text();assert text.count(anchor)==1
    history.write_text(text.replace(anchor,anchor+"\n    folders.append('pride-menu-publish83-baseline')"))
    launcher.write_text(after);out=base/'publication';out.mkdir()
    checks=dict(package83_selected='dist/installed-preview83' in launcher.read_text(),
                only_launcher_package_selection_changed=launcher.read_text()==before.replace('dist/installed-preview74','dist/installed-preview83'),
                installed_assets_helper_and_old_binary_unchanged=all(digest(ROOT/p)==sha for p,sha in protected.items()))
    paths=[Path(__file__),bp,*proofs,packagepath,launcher,history,candidate,archive/'report.json',*protected_paths]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,
                full_first_level_fidelity_complete=False,current_build_saves_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PUBLISHED',build['binary_sha256'],checks,flush=True)


if __name__=='__main__':main()
