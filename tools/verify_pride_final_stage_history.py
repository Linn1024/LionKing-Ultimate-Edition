"""Check retained-map history bounds and main-scene/legacy continuation controls."""
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
    base=ROOT/'build/pride-final-arena-phase';build=base/'build-report.json';bound(build)
    arena=base/'verification/report.json';measured=bound(arena)
    prior=ROOT/'build/pride-final-combined/controls/report.json';controls=bound(prior)
    lifecycle=ROOT/'build/pride-final-combined/lifecycle/report.json';old_lifecycle=bound(lifecycle)
    out=base/'history-controls';out.mkdir();checks={};commands={}
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',TLK_FINAL_SCENE_PRESENT='1',
        TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    def run(label,template):
        folder=out/label;folder.mkdir();cmd=template.copy();cmd[0]=str(base/'player.exe')
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        with (folder/'run.log').open('wb') as log:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        commands[label]=cmd;return folder,p.returncode
    saved=base/'verification/native-0/saved.state';raw=saved.read_bytes();length=struct.unpack_from('<I',raw,20)[0]
    native=96+struct.unpack_from('<I',raw,108)[0]
    view=native+36+struct.unpack_from('<Q',raw,native+24)[0]+4
    metadata={str(at):struct.unpack_from('<I',raw,view+at)[0] for at in (8,52,56,60,64,68)}
    checks['v3_retained_map_present']=metadata['8']==3 and metadata['52']==1 and metadata['56']*metadata['60']==metadata['68']>0
    def reseal(data):
        data[152:184]=bytes(32);data[152:184]=hashlib.sha256(data[96:96+length]).digest()
        data[64:96]=bytes(32);data[64:96]=hashlib.sha256(data).digest();return data
    mutations={'map-flag':[(52,2)],'odd-row':[(56,201)],'product-overflow':[(56,65536),(60,65536)],
        'map-size':[(68,metadata['68']+1)],'rom-block':[(64,0x3fffff)],'reserved':[(76,1)],
        'inactive-with-map':[(52,0)],'history-version':[(8,4)]}
    for label,changes in mutations.items():
        data=bytearray(raw)
        for at,value in changes:struct.pack_into('<I',data,view+at,value)
        path=out/(label+'.state');path.write_bytes(reseal(data));before=digest(path)
        template=measured['commands']['native-resumed0-1'].copy();template[template.index('--load')+1]=str(path)
        _,code=run(label,template);checks[label+'_reject']=code==8;checks[label+'_input_intact']=before==digest(path)
    for name,template,reference in [
        ('legacy-final',controls['commands']['legacy-final-v1'],ROOT/'build/pride-final-combined/controls/legacy-final-v1'),
        ('legacy-owned',old_lifecycle['commands']['owned-to-revival-resumed'],ROOT/'build/pride-final-combined/lifecycle/owned-to-revival-resumed')]:
        folder,code=run(name,template);checks[name+'_exit']=code==0
        if not code:
            checks[name+'_guest']=hashes(folder/'run.log')==hashes(reference/'run.log')
            checks[name+'_client']=pixels(folder/'window.png')==pixels(reference/'window.png')
            checks[name+'_pcm']=pcm(folder/'audio.wav')==pcm(reference/'audio.wav')
    # Rewrap a genuine main-scene final7 checkpoint so its native presentation
    # history is emitted by this build, then check new v3 cold continuation.
    template=controls['commands']['legacy-final-v1'].copy();template[template.index('--frames')+1]='3904'
    template+=['--save-at','3903',str(out/'main-direct/saved.state')]
    direct,code=run('main-direct',template);checks['main_v3_save_exit']=code==0 and (direct/'saved.state').is_file()
    if checks['main_v3_save_exit']:
        resume=template.copy();i=resume.index('--save-at');del resume[i:i+3]
        resume[resume.index('--load')+1]=str(direct/'saved.state')
        cold,code=run('main-resumed',resume);checks['main_v3_load_exit']=code==0
        if not code:
            checks['main_v3_guest']=hashes(cold/'run.log')==hashes(direct/'run.log')
            checks['main_v3_client']=pixels(cold/'window.png')==pixels(direct/'window.png')
            audio=pcm(cold/'audio.wav');checks['main_v3_pcm']=bool(audio) and audio==pcm(direct/'audio.wav')[-len(audio):]
    paths=[Path(__file__),build,arena,prior,lifecycle,saved]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,metadata=metadata,commands=commands,
        rejection_scope='New-process CLI rejection and input preservation',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
