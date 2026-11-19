"""Package the walkthrough-tested development build with existing prepared data."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token-behavior50';build_path=base/'build-report.json';build=bound(build_path)
    evidence=[base/name/'report.json' for name in ('pickup-play','completion','behavior-ui3','native75','allbugs-verification')]
    for path in evidence:
        report=bound(path);assert report['result']=='PASS' and all(report['checks'].values()),path
    out=ROOT/'dist/installed-preview50';out.mkdir()
    previous=ROOT/'dist/installed-preview47';old_report=previous/'package-report.json';bound(old_report)
    names=[p.relative_to(previous) for p in previous.rglob('*') if p.is_file() and p.name not in ('package-report.json','package.json','README.txt','LionKing.exe')]
    for name in names:
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(previous/name,target)
    shutil.copyfile(base/'player.exe',out/'LionKing.exe')
    info=json.loads((previous/'package.json').read_text());info['player_sha256']=build['binary_sha256'];info['development_build']=True
    info['save_scope']='current-build';info['full_first_level_fidelity_complete']=False
    (out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
    (out/'README.txt').write_text('Lion King development preview\n\nUse Play Installed Preview.cmd from the project root. Existing prepared\ngame data is sufficient; new installations use Setup.cmd. F12 opens the\nSNES/Mega Drive resource tree. Continue-token artwork, palette, animation\nand pickup voice have separate choices. Behavior changes restart the level.\n\nThis hybrid uses compiled game code and emulated hardware/routines.\nThe full first-level fidelity work remains in progress. Development saves\nare specific to the current build. Game data and settings stay local;\nthis package contains no ROMs or extracted game assets. See licenses.\n')
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';text=launcher.read_text().replace('dist/installed-preview47','dist/installed-preview50')
    assert 'dist/installed-preview50' in text
    text=text.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'")
    candidate=base/'RunInstalledPreviewCandidate.ps1';assert not candidate.exists();candidate.write_text(text)
    paths=[Path(__file__),build_path,old_report,*evidence,launcher,ROOT/'Play Installed Preview.cmd',candidate]
    report=dict(result='PACKAGED_FOR_VERIFICATION',binary_exact=digest(out/'LionKing.exe')==build['binary_sha256'],
                installed_assets_changed=False,save_compatibility_scope='current-build',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'package-report.json').write_text(json.dumps(report,indent=2)+'\n');print('PACKAGED',info['player_sha256'],flush=True)


if __name__=='__main__':main()
