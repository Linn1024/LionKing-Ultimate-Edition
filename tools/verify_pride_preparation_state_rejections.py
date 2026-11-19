"""Check prepared-bank/decoder-cache preflight, with a matching positive control.

Re-sealed fixtures exercise explicit scalar/length/source validators, rather
than relying only on checksum errors. Same-process rollback is still separate.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-preparation-state';out=base/'rejections';out.mkdir(exist_ok=True)
    source=base/'matrix/256-native-4668-aot-lle/checkpoint.private-state'
    raw=source.read_bytes();assert raw[:8]==b'PRPSAVE1'
    native_size,history_size,cache_size=struct.unpack_from('<III',raw,len(raw)-24)
    start=512+native_size+history_size
    assert start+cache_size+32==len(raw) and raw[start:start+8]==b'PRPREP01'
    recipe_size=struct.unpack_from('<I',raw,start+84)[0]
    assert recipe_size==7*(12+25+20+2*76+12)
    def seal(data,cache=True):
        data=bytearray(data)
        if cache:
            data[start+48:start+80]=bytes(32)
            data[start+48:start+80]=hashlib.sha256(data[start:start+cache_size]).digest()
        data[56:88]=bytes(32);data[56:88]=hashlib.sha256(data).digest();return data
    cases={}
    for name,offset,value in (
        ('cache-version',8,2),('cache-size',12,cache_size+1),('cache-field',80,4669),
        ('recipe-size',84,recipe_size+1),('bank-size',88,1),('cache-reserved',92,1),
        ('recipe-source',96,0),('recipe-destination',100,0),('recipe-output-size',104,1),
        ('recipe-register-range',96+37+4,65536),('recipe-stack-range',96+37+16,0x100),
        ('recipe-dma-mode',96+57+40,8),('recipe-dma-boolean',96+57+44,2),
        ('recipe-port',96+209,0),('recipe-ready',96+213,0),('recipe-capturing',96+217,1)):
        data=bytearray(raw);struct.pack_into('<I',data,start+offset,value);cases[name]=seal(data)
    for name,offset in (('cache-build',16),('cache-checksum',48)):
        data=bytearray(raw);data[start+offset]^=1;cases[name]=seal(data,name!='cache-checksum')
    for name,offset,value in (('footer-version',len(raw)-12,2),('footer-reserved',len(raw)-8,1),
                              ('footer-cache-size',len(raw)-16,cache_size+1)):
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);cases[name]=seal(data,False)
    # Damage the bank record while maintaining both surrounding checksums.
    bank=start+96+recipe_size
    for name,offset in (('bank-magic',0),('bank-version',8),('bank-source',16)):
        data=bytearray(raw);data[bank+offset]^=1;cases[name]=seal(data)
    cases['valid-control']=raw
    binary=base/'preparation-state-probe.exe';identity=digest(binary);results={}
    for name,data in cases.items():
        folder=out/name;folder.mkdir(exist_ok=True);state=folder/'case.private-state';state.write_bytes(data)
        profile=folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\ngraphics.sprites.checkpoints.frames = md\ngraphics.sprites.checkpoints.palette = md\n')
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        before=digest(state)
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--frames','4673','--wide','256','--input-polled',base/'neutral.polled.tape','--load',state]
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
        assert result.returncode==(0 if name=='valid-control' else 8),(name,result.returncode)
        assert digest(state)==before and not list(folder.glob('*.part*'))
        results[name]=dict(exit_code=result.returncode,record_preserved=True,
            artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,runs=results,
        binary_sha256=identity,script_sha256=digest(Path(__file__)),source_state_sha256=digest(source),
        same_process_rollback_verified=False,full_first_level_fidelity_complete=False),indent=2)+'\n')
    print(f'{len(results)-1} damaged cache/policy records rejected; valid control accepted',flush=True)


if __name__=='__main__':main()
