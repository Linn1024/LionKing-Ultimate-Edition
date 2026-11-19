"""Check legacy saves, inactive-controller neutrality and composite rejections."""
import hashlib
import json
import os
from pathlib import Path
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
    base=ROOT/'build/pride-final-combined';out=base/'controls';out.mkdir();checks={};commands={}
    build=base/'build-report.json';bound(build)
    lifecycle=base/'lifecycle/report.json';combined=bound(lifecycle)
    prior=ROOT/'build/pride-final-mixed-fade/verification/report.json';legacy=bound(prior)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    active=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    def run(label,template,env,old=False):
        folder=out/label;folder.mkdir();cmd=template.copy()
        cmd[0]=str(ROOT/('build/pride-final-mixed-fade/player.exe' if old else 'build/pride-final-combined/player.exe'))
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        with (folder/'run.log').open('wb') as log:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        commands[label]=cmd;return folder,p.returncode
    # Previous version1 final save remains readable with its native-death profile.
    resumed,code=run('legacy-final-v1',legacy['commands']['palettes-resumed10'],active)
    checks['legacy_final_v1_exit']=code==0
    previous=ROOT/'build/pride-final-mixed-fade/verification/palettes-resumed10'
    if not code:
        checks['legacy_final_v1_guest']=hashes(resumed/'run.log')==hashes(previous/'run.log')
        checks['legacy_final_v1_client']=pixels(resumed/'window.png')==pixels(previous/'window.png')
        checks['legacy_final_v1_pcm']=pcm(resumed/'audio.wav')==pcm(previous/'audio.wav')
    # The nested owned backend remains a genuine previous-format nonfinal save.
    source=base/'lifecycle/owned-to-revival/saved.state';raw=source.read_bytes();length=struct.unpack_from('<I',raw,20)[0]
    inner=out/'owned-backend.state';inner.write_bytes(raw[96:96+length])
    template=combined['commands']['owned-to-revival-resumed'].copy()
    template[template.index('--load')+1]=str(inner);template[template.index('--frames')+1]='1710'
    a,code_a=run('nonfinal-inactive-new',template,clean);b,code_b=run('nonfinal-inactive-old',template,clean,old=True)
    checks['inactive_both_exit']=code_a==code_b==0
    if not code_a and not code_b:
        checks['inactive_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks['inactive_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks['inactive_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
    # Reseal only the outer digest so the nested parser must reject its own data.
    def sealed(data):
        data[64:96]=bytes(32);data[64:96]=hashlib.sha256(data).digest();return data
    malformed={}
    data=bytearray(raw);struct.pack_into('<I',data,96+20,1701);malformed['nested-field']=sealed(data)
    data=bytearray(raw);data[96+56]^=1;malformed['nested-checksum']=sealed(data)
    data=bytearray(raw);data[96:104]=b'UNKNOWN1';malformed['nested-kind']=sealed(data)
    data=bytearray(raw);struct.pack_into('<I',data,8,3);malformed['outer-version']=sealed(data)
    for label,data in malformed.items():
        path=out/(label+'.state');path.write_bytes(data);before=digest(path)
        cmd=combined['commands']['owned-to-revival-resumed'].copy();cmd[cmd.index('--load')+1]=str(path)
        _,code=run(label,cmd,active)
        checks[label+'_reject']=code==8;checks[label+'_input_unchanged']=digest(path)==before
    paths=[Path(__file__),build,lifecycle,prior,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        rejection_scope='New-process CLI rejection and input preservation; not an interactive rollback measurement',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
