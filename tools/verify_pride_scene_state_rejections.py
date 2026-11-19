"""Exercise damaged/source-incompatible private records and save replacement.

Rejection exits and filesystem preservation are checked. This does not claim a
complete same-process rollback audit or prepared-presentation lifecycle.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def seal(data):
    data=bytearray(data);data[56:88]=bytes(32);data[56:88]=hashlib.sha256(data).digest();return data


def main():
    base=ROOT/'build/pride-scene-state';out=base/'rejections';out.mkdir(exist_ok=True)
    binary=base/'scene-state-probe.exe';source=base/'matrix/4703-aot-lle/checkpoint.private-state'
    raw=source.read_bytes();assert raw[:8]==b'PRDSAVE1';identity=digest(binary)
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\n')
    cases={'truncated':raw[:256],'trailing':raw+b'\0','native-without-context':raw[512:]}
    for name,offset,value,resign in (
        ('magic',0,0,False),('checksum',100,raw[100]^1,False),('reserved',88,1,True),
        ('build',24,raw[24]^1,True),('scene-checksum',192,raw[192]^1,True)):
        data=bytearray(raw);data[offset]=value;cases[name]=seal(data) if resign else data
    for name,offset,value in (('field-link',20,4704),('boolean',228,2),
                              ('native-version',520,99),('native-field-link',524,4704)):
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);cases[name]=seal(data)
    data=bytearray(raw);data[112]^=1;data[192:224]=bytes(32)
    data[192:224]=hashlib.sha256(data[96:224]).digest();cases['scene-program']=seal(data)
    cases['policy']=raw
    results={}
    def env_for(folder):
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        return env
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--frames','5400','--input-polled',base/'neutral.polled.tape']
    for name,data in cases.items():
        folder=out/name;folder.mkdir(exist_ok=True);path=folder/'invalid.private-state';path.write_bytes(data)
        before=digest(path);env=env_for(folder)
        if name=='policy':env['TLK_SCENE_RESTORE_ROAR_ZERO']='0'
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(list(map(str,[*command,'--load',path])),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
        assert result.returncode==8,(name,result.returncode)
        assert digest(path)==before and not list(folder.glob('*.part*'))
        results[name]=dict(exit_code=8,record_preserved=True,artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
    folder=out/'unsupported-save';folder.mkdir(exist_ok=True);path=folder/'existing.private-state';path.write_bytes(raw)
    cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
         '--resource-profile',profile,'--frames','4500','--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
         '--save-at','4500',path]
    with (folder/'run.log').open('wb') as log:
        result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env_for(folder),stdout=log,stderr=subprocess.STDOUT,timeout=120)
    assert result.returncode==8 and path.read_bytes()==raw and not list(folder.glob('*.part*'))
    results['unsupported-save']=dict(exit_code=8,previous_valid_save_preserved=True,
        artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,runs=results,
        binary_sha256=identity,source_state_sha256=digest(source),script_sha256=digest(Path(__file__)),
        same_process_rollback_verified=False,full_first_level_fidelity_complete=False),indent=2)+'\n')
    print(str(len(results))+' rejection/save-preservation cases PASS',flush=True)


if __name__=='__main__':main()
