"""Resolve the native menu's installation difference with identical sound backends."""
import json
from pathlib import Path
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-singlepass/plain-native';raw_path=base/'verified/report.json';raw=bound(raw_path)
    assert raw['result']=='INCOMPLETE' and [k for k,v in raw['checks'].items() if not v]==['aot-menu-gl/whole_client']
    build_path=base/'build-report.json';build=bound(build_path);prior_path=ROOT/'build/pride-reset/fixed4/build-report.json';prior=bound(prior_path)
    out=base/'ready-reference';out.mkdir();before=ROOT/'build/pride-reset/fixed4/native-sdl.exe';assert digest(before)==prior['runs']['sdl']['binary_sha256']
    backend=base/'genesis_plus_gx_libretro.dll';binary=out/'reference.exe';shutil.copy2(before,binary);shutil.copy2(backend,out/backend.name)
    author=base/'verified/aot-menu-gl/before';candidate=base/'verified/aot-menu-gl/after'
    assert 'MD sound library unavailable' in (author/'run.log').read_text()
    assert 'MD audio ready' in (candidate/'run.log').read_text()
    cmd=[str(binary)]+[v.replace(str(author),str(out)) for v in raw['commands']['aot-menu-gl/before'][1:]]
    (out/'host.ini').write_bytes((author/'host.ini').read_bytes())
    import os
    env=os.environ.copy();env.pop('SDL_VIDEODRIVER',None)
    with (out/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    assert not r.returncode,r.returncode
    assert 'MD audio ready' in (out/'run.log').read_text()
    checks=dict(raw['checks']);checks['aot-menu-gl/whole_client']=pixels(out/'window.png')==pixels(candidate/'window.png')
    checks['ready_reference/pcm']=wav_data(out/'audio.wav')==wav_data(candidate/'audio.wav')
    checks['ready_reference/native_image']=pixels(out/'guest.png')==pixels(candidate/'guest.png')
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    paths=[Path(__file__),raw_path,build_path,prior_path,before,backend,ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py']
    report=dict(result='PASS',checks=checks,command=cmd,binary_sha256=build['binary_sha256'],reference_binary_sha256=digest(binary),presentations=raw['presentations'],
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS ordinary native frontend:',len(checks),'checks',flush=True)


if __name__=='__main__':main()
