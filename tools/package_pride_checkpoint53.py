"""Package the qualified checkpoint update with its exact declared timing scope."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-checkpoint-capability53';buildpath=base/'build-report.json';build=bound(buildpath)
    runtime=ROOT/'build/pride-checkpoint-animation52'
    evidence=[base/name/'report.json' for name in ('completion','windows-scope')]
    evidence += [runtime/name/'report.json' for name in ('cadence-qualification','source-mixtures-qualification','windows-ui','native75','allbugs-verification')]
    for path in evidence:
        report=bound(path);assert report['result']=='PASS' and all(report['checks'].values()),path
    out=ROOT/'dist/installed-preview53';out.mkdir()
    previous=ROOT/'dist/installed-preview50';oldreport=previous/'package-report.json';bound(oldreport)
    for original in previous.rglob('*'):
        if not original.is_file() or original.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
        target=out/original.relative_to(previous);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,target)
    shutil.copyfile(base/'player.exe',out/'LionKing.exe')
    info=json.loads((previous/'package.json').read_text());info['player_sha256']=build['binary_sha256'];info['development_build']=True
    info['save_scope']='current-build';info['full_first_level_fidelity_complete']=False
    info['checkpoint_animation_scope']='MD 6/21/6-update blink sequence and repeating idle; native game update scheduling retained'
    (out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
    (out/'README.txt').write_text('Lion King development preview\n\nUse Play Installed Preview.cmd from the project root. Existing prepared\ngame data is sufficient; new installations use Setup.cmd. F12 opens the\nSNES/Mega Drive resource tree. Checkpoint artwork, palette, animation and\nsound have separate choices. MD checkpoint animation repeats its original\n6/21/6-update blink sequence, retaining native game update scheduling.\nBehavior changes restart the level; H shows each choice\'s supported scope.\n\nThis hybrid uses compiled game code and emulated hardware/routines.\nFull first-level fidelity work remains in progress. Saves belong to the\ncurrent development build. This package contains no ROMs or extracted\ngame assets. See licenses.\n')
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';text=launcher.read_text();assert 'dist/installed-preview50' in text
    text=text.replace('dist/installed-preview50','dist/installed-preview53')
    text=text.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'")
    candidate=base/'RunInstalledPreviewCandidate.ps1';assert not candidate.exists();candidate.write_text(text)
    paths=[Path(__file__),buildpath,oldreport,*evidence,launcher,ROOT/'Play Installed Preview.cmd',candidate]
    report=dict(result='PACKAGED_FOR_VERIFICATION',binary_exact=digest(out/'LionKing.exe')==build['binary_sha256'],
                installed_assets_changed=False,save_compatibility_scope='current-build',
                native75_and_allbugs_scope='52 runtime;53 retains all321 non-resource inputs and changes only one capability description',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'package-report.json').write_text(json.dumps(report,indent=2)+'\n');print('PACKAGED',info['player_sha256'],flush=True)


if __name__=='__main__':main()
