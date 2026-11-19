"""Check old 256-wide records and reject malformed width-bearing saves."""
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
    base=ROOT/'build/pride-final-wide';out=base/'controls';out.mkdir();checks={};commands={}
    build=base/'build-report.json';bound(build)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',TLK_FINAL_SCENE_PRESENT='1',
        TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    def run(label,template):
        folder=out/label;folder.mkdir();cmd=template.copy();cmd[0]=str(base/'player.exe')
        if '--save-at' in cmd:
            i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            if flag in cmd:cmd[cmd.index(flag)+1]=str(folder/name)
        with (folder/'run.log').open('wb') as log:
            p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        commands[label]=cmd;return folder,p.returncode
    paths=[Path(__file__),build]
    for label,report,key in [
        ('legacy-v1',ROOT/'build/pride-final-mixed-fade/verification/report.json','palettes-resumed10'),
        ('legacy-v2',ROOT/'build/pride-final-arena-phase/verification/report.json','native-resumed0-1')]:
        data=bound(report);paths.append(report);template=data['commands'][key]
        folder,code=run(label,template);previous=Path(template[template.index('--dump-window')+1]).parent
        checks[label+'_exit']=code==0
        if not code:
            checks[label+'_guest']=hashes(folder/'run.log')==hashes(previous/'run.log')
            checks[label+'_client']=pixels(folder/'window.png')==pixels(previous/'window.png')
            checks[label+'_pcm']=pcm(folder/'audio.wav')==pcm(previous/'audio.wav')
    report=base/'verification/report.json';wide=bound(report);paths.append(report)
    original=base/'verification/native-0/saved.state';raw=original.read_bytes();paths.append(original)
    def seal(data):
        data[64:96]=bytes(32);data[64:96]=hashlib.sha256(data).digest();return data
    variants={}
    for name,offset,value in [('version',8,4),('width',36,256),('side-size',40,0),
                              ('backend',44,1),('reserved',48,1)]:
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);variants[name]=seal(data)
    data=bytearray(raw);data[-4*64*224*4+64*224*4]=1;variants['absent-target']=seal(data)
    data=bytearray(raw[:-4]);struct.pack_into('<I',data,16,len(data));variants['short-sides']=seal(data)
    for name,data in variants.items():
        path=out/(name+'.state');path.write_bytes(data);before=digest(path)
        template=wide['commands']['native-resumed0-1'].copy()
        template[template.index('--load')+1]=str(path)
        _,code=run(name,template)
        checks[name+'_rejected']=code==8;checks[name+'_input_preserved']=digest(path)==before
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        rejection_scope='New-process CLI rejection; no interactive rollback claim',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
