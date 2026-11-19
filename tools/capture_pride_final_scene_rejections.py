"""Reject damaged envelopes, banks, guest payloads and changed source settings."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def seal(data,offset=64):
    data[offset:offset+32]=bytes(32);data[offset:offset+32]=hashlib.sha256(data).digest()


def main():
    base=ROOT/'build/pride-final-scene-lifecycle-probe';out=base/'rejections';out.mkdir()
    bound(base/'build-report.json');reference=ROOT/'build/pride-final-scene-save-probe/capture/report.json';report=bound(reference)
    saved=reference.parent/'100/saved.state';original=saved.read_bytes();identity=digest(saved)
    ns,ps,bs=struct.unpack_from('<III',original,20);private=96+ns;bank=private+ps
    cases=[]
    b=bytearray(original);b[-1]^=1;cases.append(('outer_checksum',b,{}))
    b=bytearray(original);struct.pack_into('<I',b,16,len(b)+1);seal(b);cases.append(('outer_length',b,{}))
    b=bytearray(original);b[private+108]|=128
    record=bytearray(b[private:private+ps]);seal(record,48);b[private:private+ps]=record;seal(b)
    cases.append(('private_semantics',b,{}))
    assert bs>128
    b=bytearray(original);b[bank+128]^=1;seal(b);cases.append(('bank_checksum',b,{}))
    b=bytearray(original);b[96+ns-1]^=1;seal(b);cases.append(('native_checksum',b,{}))
    cases.append(('truncated',bytearray(original[:96]),{}))
    cases.append(('source_mode',bytearray(original),{'TLK_CONTINUE_FAST_RELOAD':'0'}))
    cases.append(('disabled',bytearray(original),{'TLK_CONTINUE_TRANSITION':'0'}))
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};checks={};commands=[]
    for name,data,change in cases:
        folder=out/name;folder.mkdir();path=folder/'invalid.state';path.write_bytes(data)
        cmd=report['commands'][1].copy();cmd[0]=str(base/'player.exe');cmd[cmd.index('--load')+1]=str(path)
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),
            TLK_CONTINUE_TRANSITION='1',TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        env.update(change)
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW)
        log=(folder/'run.log').read_text(errors='replace')
        checks[name+'/rejected']=run.returncode==8 and 'cannot load state' in log
        checks[name+'/no_guest_load_reported']='loaded_state=' not in log
        checks[name+'/no_temporary_leftover']=not any('final-load' in p.name or 'final-native' in p.name or 'final-part' in p.name for p in folder.iterdir())
        commands.append(cmd);print(name,run.returncode,flush=True)
    checks['original_save_unchanged']=digest(saved)==identity
    paths=[Path(__file__),base/'build-report.json',reference,saved]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'checks',flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
