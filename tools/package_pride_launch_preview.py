"""Package the current first-level development build without replacing installed players."""
import json
from pathlib import Path
import shutil

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-launch2';build_path=base/'build-report.json';build=bound(build_path)
    evidence=[base/'probe/report.json',base/'switch/report.json']
    for path in evidence:
        report=bound(path);assert report['result']=='PASS' and all(report['checks'].values()),path
    for path,sha in build['production_sha256'].items():assert digest(ROOT/path)==sha,path
    out=ROOT/'dist/development-preview';out.mkdir();exe=base/'player.exe';assert digest(exe)==build['binary_sha256']
    shutil.copy2(exe,out/'LionKing.exe');shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    shutil.copy2(base/'save-compatibility.json',out/'save-compatibility.json')
    source=ROOT/'build/pride-source-live/seeded/resources.ini';preset=ROOT/'profiles/pride-development-preview.ini';assert not preset.exists()
    preset.write_bytes(b'; Development preview for Pride Lands; the full-level audit is still open.\n'+source.read_bytes()+b'gameplay.levels.pride_lands.health_death = md\n')
    (out/'README.txt').write_text('Development preview for Pride Lands\n\nRun Play Development Preview.cmd from the project folder.\nF12 opens the SNES/Mega Drive resource tree. Apply source changes there;\ngameplay changes can restart the level. Settings and save slots are kept\nunder settings/development-preview, separately from the installed player.\n\nThis preview is for first-level testing. The first-level fidelity audit,\nremaining levels and cross-format save migration are not complete.\nThe normal Play.cmd launchers still use the older installed player.\n',encoding='utf-8')
    paths=[Path(__file__),build_path,source,preset,ROOT/'Play Development Preview.cmd',*evidence]
    report=dict(result='PACKAGED',binary_sha256=digest(out/'LionKing.exe'),save_compatibility_sha256=build['save_compatibility_sha256'],
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.iterdir() if p.is_file()},
                default_installed_player_replaced=False,experimental_preview=True,full_first_level_fidelity_complete=False)
    (base/'preview-package.json').write_text(json.dumps(report,indent=2)+'\n');print('Development preview packaged; normal player unchanged',flush=True)


if __name__=='__main__':main()
