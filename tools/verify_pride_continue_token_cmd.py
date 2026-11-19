"""Exercise the public CMD entry point with default installed data at the Sun."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    base=ROOT/'build/pride-continue-token47';publication=base/'publication/report.json';assert bound(publication)['result']=='PASS'
    runtime=base/'artwork-verification/report.json';prior=bound(runtime)
    out=base/'cmd-verification';out.mkdir();settings=out/'settings';settings.mkdir()
    source=base/'full-route/aot'
    for before,after in [('host.ini','game.ini'),('resources.ini','resources.ini')]:shutil.copyfile(source/before,settings/after)
    (settings/'last_session.rec').write_bytes(b'preserve an existing recording')
    protected={p.name:digest(p) for p in settings.iterdir()}
    full=ROOT/'build/pride-sprite-fresh44/runtime-verification/report.json';reference=bound(full)
    template=reference['commands']['full-aot'];tape=Path(template[template.index('--input-polled')+1])
    cmd=['cmd.exe','/d','/c','call',str(ROOT/'Play Installed Preview.cmd'),'-SettingsDirectory',str(settings),
         '-Frames','2520','-InputTape',str(tape),'-NoPace','-NoAudio','-WindowCapture',str(out/'window.png'),
         '-SceneCapture',str(out/'scene.json'),'-AudioCapture',str(out/'audio.wav')]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    clean['PATH']=str(Path(os.environ['SystemRoot'])/'System32')
    with (out/'run.log').open('wb') as log:
        rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    checks={'public_cmd_exit':rc==0}
    expected=re.search(r'frame=2520 frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(Path(template[template.index('--dump-window')+1]).parent/'run.log').read_text())
    checks['guest_endpoint_reference']=hashes(settings/'last-launch.log')==dict(frame_sha256=expected.group(1),wram_sha256=expected.group(2))
    checks['sun_artwork_matches_qualified_cold_window']=digest(out/'window.png')==digest(base/'artwork-verification/both/window.png')
    checks['scene_matches_qualified_cold_scene']=digest(out/'scene.json')==digest(base/'artwork-verification/both/scene.json')
    audio=ROOT/'build/pride-effect-coverage/sun-owners2/control/audio.wav'
    checks['whole_poweron_audio_preserved']=digest(out/'audio.wav')==digest(audio)
    checks['settings_and_recording_preserved']=all(digest(settings/name)==sha for name,sha in protected.items())
    checks['installed_cache_and_audio_backend_loaded']=all(word in (settings/'last-launch.log').read_text() for word in ('resource_cache=loaded','MD audio ready'))
    paths=[Path(__file__),publication,runtime,full,audio,ROOT/'scripts/RunInstalledPreview.ps1',ROOT/'Play Installed Preview.cmd']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,
                default_installed_data_used=True,user_settings_directory_untouched=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
