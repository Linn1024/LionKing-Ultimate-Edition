"""Reject malformed prepared histories, including re-sealed pointer encodings.

Checks exit status and file preservation; full same-process rollback remains a
separate requirement. No process address is placed into these fixtures.
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
    base=ROOT/'build/pride-prepared-state';out=base/'rejections';out.mkdir(exist_ok=True)
    source=base/'matrix/256-native-4700-aot-lle/checkpoint.private-state';raw=source.read_bytes()
    assert raw[:8]==b'PRDSAVE1';binary=base/'prepared-state-probe.exe';identity=digest(binary)
    native_len,history_len=struct.unpack_from('<II',raw,len(raw)-16);start=512+native_len
    assert start+history_len+24==len(raw) and raw[start:start+8]==b'PRDHIST1'
    def seal(data,history=True):
        data=bytearray(data)
        if history:
            data[start+48:start+80]=bytes(32)
            data[start+48:start+80]=hashlib.sha256(data[start:start+history_len]).digest()
        data[56:88]=bytes(32);data[56:88]=hashlib.sha256(data).digest();return data
    cases={}
    for name,offset,value,history in (
        ('history-version',start+8,99,True),('history-size',start+12,history_len+4,True),
        ('history-field',start+96,4701,True),('history-age',start+100,269,True),
        ('width',start+104,257,True),('column',start+108,33,True),
        ('early-release',start+124,1,True),('missing-recipe',start+128,0,True),
        ('piece-count',start+144,513,True),('line-vram-index',start+288,4,True),
        ('retained-map-kind',start+history_len-8,3,True),
        ('retained-map-offset',start+history_len-4,1,True),
        ('footer-version',len(raw)-8,2,False),('footer-reserved',len(raw)-4,1,False),
        ('footer-native-length',len(raw)-16,native_len+1,False),
        ('native-version',512+8,99,False)):
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);cases[name]=seal(data,history)
    frame_start=96+15*4;piece_at=frame_start+224*2216+4+0x20000
    count=struct.unpack_from('<I',raw,start+piece_at)[0];assert count<=512
    map_kind=piece_at+8+count*48+8+4+256*224*4+8+12
    assert struct.unpack_from('<I',raw,start+map_kind)[0] in (1,2)
    for name,offset,value in (('frozen-map-kind',map_kind,3),('frozen-map-offset',map_kind+4,0xffffffff)):
        data=bytearray(raw);struct.pack_into('<I',data,start+offset,value);cases[name]=seal(data)
    for name,offset in (('reserved-history',start+84),('graphics-identity',start+80),('source-identity',start+16),('history-checksum',start+48)):
        data=bytearray(raw);data[offset]^=1;cases[name]=seal(data,name!='history-checksum')
    cases['valid-control']=raw;cases['viewport-policy']=raw;cases['render-policy']=raw;cases['graphics-policy']=raw
    results={}
    for name,data in cases.items():
        folder=out/name;folder.mkdir(exist_ok=True);state=folder/'bad.private-state';state.write_bytes(data)
        profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = '+('md' if name=='viewport-policy' else 'snes')+'\ngraphics.sprites.checkpoints.frames = md\ngraphics.sprites.checkpoints.palette = md\n')
        if name=='graphics-policy':profile.write_text(profile.read_text()+'graphics.sprites.simba.cub.palette = md\n')
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        if name=='render-policy':env['TLK_SCENE_RENDER_ENABLE']='0'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        before=digest(state)
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--frames','4701','--wide','256','--input-polled',base/'neutral.polled.tape','--load',state]
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
        assert run.returncode==(0 if name=='valid-control' else 8),(name,run.returncode)
        assert digest(state)==before and not list(folder.glob('*.part*'))
        results[name]=dict(exit_code=run.returncode,record_preserved=True,
            artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,runs=results,
        binary_sha256=identity,script_sha256=digest(Path(__file__)),source_state_sha256=digest(source),
        same_process_rollback_verified=False,cross_graphics_load_verified=False,full_first_level_fidelity_complete=False),indent=2)+'\n')
    print(str(len(results)-1)+' malformed prepared-history/policy cases rejected; valid control accepted; no file changes or temporary leaks',flush=True)


if __name__=='__main__':main()
