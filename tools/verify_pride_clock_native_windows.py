"""Compare ordinary native Windows hosts before and after the clock-state repair."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def main():
    base=ROOT/'build/pride-restart-clock/native';out=base/'windows';out.mkdir(exist_ok=True)
    build_path=base/'build-report.json';build=json.loads(build_path.read_text())
    before=ROOT/'engine/build-win/tlk_sdl.exe';after=base/'native-sdl.exe'
    assert digest(before)==build['production_sha256']['engine/build-win/tlk_sdl.exe']
    assert digest(after)==build['runs']['sdl']['binary_sha256']
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={};checks={}
    for mode in ('aot','lle'):
        folders=[]
        for name,binary in (('before',before),('after',after)):
            folder=out/(mode+'-'+name);folder.mkdir(exist_ok=True);folders.append(folder)
            config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
            command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--config',config,
                '--input',tape,'--frames',3000,'--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
                '--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100]
            if mode=='lle':command+=['--lle']
            commands[mode+'-'+name]=list(map(str,command))
            with (folder/'run.log').open('wb') as log:
                result=subprocess.run(commands[mode+'-'+name],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=300)
            assert not result.returncode,(mode,name,result.returncode)
        a,b=folders
        checks[mode+'/guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[mode+'/client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[mode+'/pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,tape,ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py')}
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,
        source_sha256=sources,before_binary_sha256=digest(before),after_binary_sha256=digest(after),
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
