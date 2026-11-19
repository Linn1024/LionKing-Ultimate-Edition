"""Stage verified independent menu effects; shared public launcher stays74."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-output83';bp=base/'build-report.json';build=bound(bp)
    proofs=[base/name/'report.json' for name in ('route','resume','windows-ui')]
    proofs += [ROOT/'build'/name/'report.json' for name in ('pride-menu-output83-owner-component','pride-menu-output83-controller','pride-menu-output84-isolation')]
    for p in proofs:
        r=bound(p);assert r['result']=='PASS' and all(r.get('checks',{'pass':True}).values()),p
    previous=ROOT/'dist/installed-preview74';old=previous/'package-report.json';bound(old)
    out=ROOT/'dist/installed-preview83';out.mkdir()
    for p in previous.rglob('*'):
        if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
        q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    shutil.copy2(base/'player.exe',out/'LionKing.exe')
    info=json.loads((previous/'package.json').read_text());info['player_sha256']=build['binary_sha256']
    info['title_menu_audio_scope']='Independent title cursor/selection and sampled Options adjustment/return; verified dry native voices replaced at output, original queue retained'
    info['current_native_owner_schema']=3
    (out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
    (out/'README.txt').write_text('Lion King Windows development preview83\n\nSetup.cmd prepares game data from your ROMs. Existing prepared assets work.\nF12 opens the SNES/Mega Drive resource tree. Sound effects include separate\ntitle cursor, title selection, Options adjustment and Options return choices.\nNative menu timing and processing remain intact; selected dry native voices\nare replaced at audio output. Music and gameplay choices are independent.\nAudio source changes restart the level.\n\nCompiled game code and remaining emulated routines/hardware are used.\nFull first-level fidelity work continues. Saves belong to the current build.\nNo ROMs or extracted game assets are bundled. See licenses.\n')
    launcher=ROOT/'scripts/RunInstalledPreview.ps1';text=launcher.read_text();assert text.count('dist/installed-preview74')==1
    text=text.replace('dist/installed-preview74','dist/installed-preview83').replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'")
    candidate=base/'RunInstalledPreviewCandidate.ps1';assert not candidate.exists();candidate.write_text(text)
    paths=[Path(__file__),bp,*proofs,old,launcher,candidate]
    report=dict(result='PACKAGED_FOR_VERIFICATION',published=False,native75_and_allbugs_pending=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'package-report.json').write_text(json.dumps(report,indent=2)+'\n');print('PACKAGED',build['binary_sha256'],flush=True)


if __name__=='__main__':main()
