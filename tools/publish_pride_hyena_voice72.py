"""Publish the qualified local development package through the shared launcher."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-hyena-voice72';bp=base/'build-report.json';build=bound(bp)
    proofs=[base/name/'report.json' for name in ('native75','allbugs-verification','completion','voice-audible','voice-ui','voice-resume-qualification','package-play2')]
    proofs.append(ROOT/'build/pride-hyena-voice72-component/report.json')
    for path in proofs:
        report=bound(path);assert report['result']=='PASS' and all(report.get('checks',{'pass':True}).values()),path
    assert build['unchanged_public65_inputs']==317 and len(build['link_inputs_sha256'])==322
    assert all(digest(ROOT/name)==sha for name,sha in build['link_inputs_sha256'].items())
    generation=ROOT/'build/pride-hyena-voice71-generation/generation-report.json';g=bound(generation)
    assert g['result']=='GENERATED' and g['program_contract_sha256']=='6ac162f5d788d7abb8b27808677a2f4bb5217f129d69232f3a35d58cb9cde304'
    for p in (base/'voice-fight/report.json',base/'voice-resume/report.json'):bound(p)
    fight=json.loads((base/'voice-fight/report.json').read_text())
    assert [k for k,v in fight['checks'].items() if not v]==['md_voice_audible_before_native_animation_cue']
    assert not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    packagepath=ROOT/'dist/installed-preview72/package-report.json';bound(packagepath)
    assert digest(ROOT/'dist/installed-preview72/LionKing.exe')==build['binary_sha256']
    for label in ('audio','resources'):assert '-DTLK_HYENA_VOICE_ENTRY_AVAILABLE=1' in build['compiles'][label]
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';history=ROOT/'tools/pride_arena_history.py';candidate=base/'RunInstalledPreviewCandidate.ps1'
    before=launcher.read_text();assert before.count('dist/installed-preview65')==1
    after=before.replace('dist/installed-preview65','dist/installed-preview72')
    fixed="$projectRoot = '"+str(ROOT)+"'";assert candidate.read_text()==after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',fixed)
    protected_paths=[ROOT/'game-data/install.json',ROOT/'dist/PrepareSpriteAssets.exe',ROOT/'dist/installed-preview65/LionKing.exe']
    protected={p.relative_to(ROOT).as_posix():digest(p) for p in protected_paths}
    archive=ROOT/'build/pride-hyena-publish72-baseline';archive.mkdir();rows={}
    names=['scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-hyena-voice-timing.md','docs/launchers.md','README.md','engine/docs/devlog.md']
    for name in names:
        p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
    (archive/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
    anchor="    folders.append('pride-hyena-voice71-baseline')";text=history.read_text();assert text.count(anchor)==1
    history.write_text(text.replace(anchor,anchor+"\n    folders.append('pride-hyena-publish72-baseline')"))
    launcher.write_text(after);out=base/'publication';out.mkdir()
    checks=dict(package72_selected='dist/installed-preview72' in launcher.read_text(),
                only_launcher_package_selection_changed=launcher.read_text()==before.replace('dist/installed-preview65','dist/installed-preview72'),
                installed_assets_helper_and_old_binary_unchanged=all(digest(ROOT/p)==sha for p,sha in protected.items()))
    paths=[Path(__file__),bp,generation,*proofs,packagepath,launcher,history,candidate,archive/'report.json',*protected_paths]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,
                full_first_level_fidelity_complete=False,current_build_saves_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PUBLISHED',build['binary_sha256'],checks,flush=True)


if __name__=='__main__':main()
