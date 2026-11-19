"""Select corrected118 only after current complete gates and installed replay pass."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-resource-tree118';bp=base/'build-report.json';b=bound(bp)
    proofs=[base/name/'report.json' for name in ('routes99','parent-verification','windows-ui119','package-play','native75','allbugs-verification')]
    proofs += [ROOT/'build'/name/'report.json' for name in ('pride-hyena-probe103-original','pride-hyena-probe103-component','pride-hyena-probe103/fights104','pride-hyena-probe103/windows-ui-qualification104')]
    for p in proofs:
        r=bound(p);assert r['result']=='PASS' and all(r['checks'].values()),p
    assert bound(base/'native75/report.json')['route_count']==75
    assert len(b['link_inputs_sha256'])==323 and b['unchanged_candidate103_inputs']==322
    assert all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
    assert not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    package=ROOT/'dist/installed-preview118/package-report.json';bound(package)
    assert digest(package.parent/'LionKing.exe')==b['binary_sha256']
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';history=ROOT/'tools/pride_arena_history.py'
    before=launcher.read_text();assert before.count('dist/installed-preview86')==1
    after=before.replace('dist/installed-preview86','dist/installed-preview118')
    candidate=base/'RunInstalledPreviewCandidate.ps1'
    assert candidate.read_text()==after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'")
    protected_paths=[ROOT/'game-data/install.json',ROOT/'dist/PrepareSpriteAssets.exe',ROOT/'dist/installed-preview86/LionKing.exe']
    protected={p.relative_to(ROOT).as_posix():digest(p) for p in protected_paths}
    archive=ROOT/'build/pride-resource-publish123-baseline';archive.mkdir();rows={}
    names=['scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','docs/resource-tree-inheritance.md','docs/pride-hyena-probe.md','docs/launchers.md','README.md','engine/docs/devlog.md']
    for name in names:
        p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
    (archive/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
    anchor="    folders.append('pride-resource-tree118-baseline')";s=history.read_text();assert s.count(anchor)==1
    history.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-resource-publish123-baseline')"))
    launcher.write_text(after);out=base/'publication';out.mkdir()
    checks=dict(corrected118_selected='dist/installed-preview118' in launcher.read_text(),only_package_selection_changed=launcher.read_text()==after,
                installed_data_helper_and_old_public_binary_unchanged=all(digest(ROOT/p)==sha for p,sha in protected.items()))
    paths=[Path(__file__),bp,*proofs,package,launcher,history,candidate,archive/'report.json',*protected_paths]
    (out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,full_first_level_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
    print('PUBLISHED',b['binary_sha256'],checks,flush=True)


if __name__=='__main__':main()
