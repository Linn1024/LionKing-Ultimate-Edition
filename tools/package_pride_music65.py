"""Prepare a candidate installed-data package without changing the public launcher."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-music-output65';bp=base/'build-report.json';build=bound(bp)
    evidence=[base/name/'report.json' for name in ('component','completion','lifecycle','audio-device','windows-ui')]
    for p in evidence:
        report=bound(p);assert report['result']=='PASS' and all(report.get('checks',{'component':True}).values()),p
    previous=ROOT/'dist/installed-preview53';old=previous/'package-report.json';bound(old)
    out=ROOT/'dist/installed-preview65';out.mkdir()
    for p in previous.rglob('*'):
        if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
        q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    shutil.copyfile(base/'player.exe',out/'LionKing.exe')
    info=json.loads((previous/'package.json').read_text());info['player_sha256']=build['binary_sha256']
    info['development_build']=True;info['save_scope']='current-build';info['full_first_level_fidelity_complete']=False
    info['pride_music_output_scope']='Verified original music voice ownership; SNES driver runs unchanged; dry output replacement in verified zero-echo Pride/Continue contexts'
    (out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
    (out/'README.txt').write_text('Lion King Windows development preview\n\nUse Play Installed Preview.cmd from the project root after publication.\nSetup.cmd prepares game data from your ROMs. Existing prepared assets are\nsufficient for this update. F12 opens the SNES/Mega Drive resource tree;\naudio source changes restart the level. Pride music replacement preserves\nthe original game/sound-driver execution and independent effect choices.\n\nThis hybrid uses compiled game code and emulated hardware/routines.\nFull first-level fidelity work remains in progress. Development saves\nbelong to the current build; older saves may be rejected. This package\ncontains no game ROMs or extracted game assets. See licenses.\n')
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';text=launcher.read_text();assert text.count('dist/installed-preview53')==1
    text=text.replace('dist/installed-preview53','dist/installed-preview65').replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'")
    candidate=base/'RunInstalledPreviewCandidate.ps1';assert not candidate.exists();candidate.write_text(text)
    paths=[Path(__file__),bp,old,*evidence,launcher,candidate,ROOT/'Play Installed Preview.cmd']
    report=dict(result='PACKAGED_FOR_VERIFICATION',binary_exact=digest(out/'LionKing.exe')==build['binary_sha256'],
                public_launcher_unchanged=True,installed_assets_or_helper_changed=False,
                native75_and_publication_pending=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'package-report.json').write_text(json.dumps(report,indent=2)+'\n');print('PACKAGED',info['player_sha256'],flush=True)


if __name__=='__main__':main()
