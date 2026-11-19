"""Exercise the installed-data checkpoint package through its candidate launcher."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    base=ROOT/'build/pride-checkpoint-capability53';out=base/'package-play';out.mkdir()
    packagepath=ROOT/'dist/installed-preview53/package-report.json';bound(packagepath)
    source=base/'completion/report.json';prior=bound(source);assert prior['result']=='PASS'
    original=source.parent/'aot';settings=out/'settings';settings.mkdir()
    for old,new in [('host.ini','game.ini'),('resources.ini','resources.ini')]:shutil.copyfile(original/old,settings/new)
    (settings/'last_session.rec').write_bytes(b'current recording retained')
    protected={p.name:digest(p) for p in settings.iterdir()}
    tape=Path(prior['commands']['aot'][prior['commands']['aot'].index('--input-polled')+1])
    powershell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    launcher=base/'RunInstalledPreviewCandidate.ps1'
    cmd=[str(powershell),'-NoProfile','-ExecutionPolicy','Bypass','-File',str(launcher),'-SettingsDirectory',str(settings),
         '-Frames','6000','-InputTape',str(tape),'-NoPace','-NoAudio','-WindowCapture',str(out/'window.png'),'-SceneCapture',str(out/'scene.json'),'-AudioCapture',str(out/'audio.wav')]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['PATH']=str(Path(os.environ['SystemRoot'])/'System32')
    with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=360,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    checks=dict(packaged_route_exit=rc==0,gameplay_endpoint=hashes(settings/'last-launch.log')==hashes(original/'run.log'),
                settings_recording_preserved=all(digest(settings/name)==sha for name,sha in protected.items()))
    for name in ('window.png','scene.json','audio.wav'):checks[name+'_exact']=digest(out/name)==digest(original/name)
    checks['no_prepared_payloads_bundled']=not any(p.suffix.lower() in ('.sfc','.smc','.md','.assets','.cache') for p in packagepath.parent.rglob('*') if p.is_file())
    paths=[Path(__file__),packagepath,source,launcher,ROOT/'game-data/install.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,uses_default_installed_data=True,
                cross_build_save_compatibility_tested=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
