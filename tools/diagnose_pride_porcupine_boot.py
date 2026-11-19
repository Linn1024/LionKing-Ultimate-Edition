"""Retain original/new compiled loader journals without editing any guest state."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-boot-diagnostic';out.mkdir()
    source=ROOT/'build/pride-porcupine37/complete-wide2/report.json'
    old=bound(source);commands={};results={}
    for label,player in [('previous35','build/pride-pickup-flight35/player.exe'),('current37','build/pride-porcupine37/player.exe')]:
        folder=out/label;folder.mkdir();diagnostics=folder/'diagnostics';diagnostics.mkdir()
        cmd=old['command'].copy();cmd[0]=str(ROOT/player)
        for flag,value in [('--frames',1100),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:
            cmd[cmd.index(flag)+1]=str(value)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(TLK_FINAL_MD_ART='1',TLK_PRIDE_DIAGNOSTICS=str(diagnostics))
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[label]=cmd;results[label]=run.returncode;print(label,run.returncode,flush=True)
    paths=[Path(__file__),source,*[ROOT/p for p in ('build/pride-pickup-flight35/player.exe','build/pride-porcupine37/player.exe')]]
    (out/'report.json').write_text(json.dumps(dict(result='OBSERVED',commands=commands,returncodes=results,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')


if __name__=='__main__':main()
