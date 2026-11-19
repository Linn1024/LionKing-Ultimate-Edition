"""Verify cold-load parity, genuine boot replay and rejection/input preservation."""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-cold-boot2';out=base/'verification';out.mkdir();checks={};commands={}
    build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-final-resource2/lifecycle/report.json';life=bound(source)
    source2=ROOT/'build/pride-final-resource2/verification/report.json';prior=bound(source2)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    def run(name,template,load=None,field=None):
        folder=out/name;folder.mkdir();cmd=template.copy();cmd[0]=str(base/'player.exe')
        cfg=folder/'host.ini';cfg.write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes());cmd[cmd.index('--config')+1]=str(cfg)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if load is not None:cmd[cmd.index('--load')+1]=str(load)
        if field is not None:cmd[cmd.index('--frames')+1]=str(field)
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        commands[name]=cmd;return folder,result.returncode
    for name,template in [('md320',life['commands']['cold-menu']),
        ('md256',prior['commands']['native-death-final']),('native-final',prior['commands']['native-final'])]:
        folder,code=run(name,template);previous=Path(template[template.index('--dump-window')+1]).parent
        checks[name+'_exit']=code==0
        if code:continue
        boot=(folder/'tlk_practice_boot.state').read_bytes()
        checks[name+'_genuine_boot_header']=boot[:8]==b'TLKSTAT1' and struct.unpack_from('<I',boot,12)[0]==0
        checks[name+'_guest']=hashes(folder/'run.log')==hashes(previous/'run.log')
        checks[name+'_client']=pixels(folder/'window.png')==pixels(previous/'window.png')
        checks[name+'_pcm']=pcm(folder/'audio.wav')==pcm(previous/'audio.wav')
        checks[name+'_no_staging_files']=not list(folder.glob('*.cold-boot*'))
    template=life['commands']['cold-menu'].copy()
    # Replay the checkpoint, including the case where the load input is the very
    # boot pathname that will be published. Its read must precede replacement.
    alias=out/'boot-alias';alias.mkdir();boot=alias/'tlk_practice_boot.state'
    shutil.copyfile(out/'md320/tlk_practice_boot.state',boot)
    cfg=alias/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
    cmd=template.copy();cmd[0]=str(base/'player.exe')
    for flag,value in [('--config',cfg),('--load',boot),('--frames','1'),('--dump-window',alias/'window.png'),
        ('--dump-scene',alias/'scene.json'),('--wav',alias/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
    with (alias/'run.log').open('wb') as log:
        result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
    commands['boot-alias']=cmd;checks['boot_alias_loads']=result.returncode==0
    fresh=out/'fresh';fresh.mkdir();direct=cmd.copy();i=direct.index('--load');del direct[i:i+2]
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:direct[direct.index(flag)+1]=str(fresh/file)
    with (fresh/'run.log').open('wb') as log:subprocess.run(direct,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    commands['fresh']=direct
    checks['boot_replays_fresh_guest']=hashes(alias/'run.log')==hashes(fresh/'run.log')
    checks['boot_replays_fresh_client']=pixels(alias/'window.png')==pixels(fresh/'window.png')
    checks['boot_replays_fresh_pcm']=pcm(alias/'audio.wav')==pcm(fresh/'audio.wav')
    for same_path in (False,True):
        folder=out/('rejected-alias' if same_path else 'rejected');folder.mkdir()
        checkpoint=folder/'tlk_practice_boot.state';checkpoint.write_bytes((out/'md320/tlk_practice_boot.state').read_bytes())
        path=checkpoint if same_path else folder/'bad.state';path.write_bytes(b'INVALID SAVE')
        before=(digest(checkpoint),digest(path));bad=cmd.copy()
        cfg=folder/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
        for flag,value in [('--config',cfg),('--load',path),('--dump-window',folder/'window.png'),
            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:bad[bad.index(flag)+1]=str(value)
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(bad,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
        label=folder.name;commands[label]=bad
        checks[label+'_rejects']=result.returncode==8
        checks[label+'_files_preserved']=(digest(checkpoint),digest(path))==before
        checks[label+'_no_staging_files']=not list(folder.glob('*.cold-boot*'))
    paths=[Path(__file__),build,source,source2]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
