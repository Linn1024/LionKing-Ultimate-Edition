"""Qualify private native-timing MD Game Over art without claiming Continue."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm

reference = ROOT/'build/pride-menu198-clocks/report.json'
ref = bound(reference)
assert ref['result']=='PASS'
base = ROOT/'build/pride-menu200-native-art'
build_path = base/'build-report.json'
bound(build_path)
out = ROOT/'build/pride-menu201-native-art'
out.mkdir()
checks = {}
commands = {}
clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for mode in ('aot','lle'):
    folder = out/mode
    folder.mkdir()
    cmd = ref['commands']['snes-'+mode].copy()
    cmd[0] = str(base/'player.exe')
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
        cmd[cmd.index(flag)+1] = str(folder/file)
    for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):
        cmd[cmd.index(flag)+1] = str(folder/file)
    env = dict(clean,SDL_VIDEODRIVER='dummy',TLK_FINAL_MD_ART='1',TLK_NATIVE_MENU200='1',TLK_MENU197=str(folder/'menu.csv'))
    with (folder/'run.log').open('wb') as f:
        rc = subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,
                            timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(mode,rc)
    commands[mode] = cmd
    control = reference.parent/'snes'/mode
    pattern = r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
    actual = re.findall(pattern,(folder/'run.log').read_text())
    expected = re.findall(pattern,(control/'run.log').read_text())
    checks[mode+'_all2501_native_guest_samples_exact'] = actual==expected and len(actual)==2501
    checks[mode+'_complete_native_pcm_exact'] = pcm(folder/'audio.wav')==pcm(control/'audio.wav')
    checks[mode+'_title_endpoint_art_retired'] = digest(folder/'window.png')==digest(control/'window.png')
    checks[mode+'_scene_endpoint_exact'] = (folder/'scene.json').read_bytes()==(control/'scene.json').read_bytes()
    checks[mode+'_native_callback_lifecycle_exact'] = (folder/'menu.csv').read_bytes()==(reference.parent/'snes/observer/menu.csv').read_bytes()
    print(mode,{k:v for k,v in checks.items() if k.startswith(mode+'_')},flush=True)
checks['mode_pcm_exact'] = pcm(out/'aot/audio.wav')==pcm(out/'lle/audio.wav')
paths = [Path(__file__),reference,build_path]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',
    checks=checks,commands=commands,
    scope='Private installed MD Game Over artwork over actual native menu-loop clocks. '
          'Guest/PCM/callback lifecycle and title retirement qualified; visual checks separate. '
          'No Continue YES/NO, save/source-switch, public capability or full menu support claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
