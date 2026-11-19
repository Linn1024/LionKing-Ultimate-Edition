"""Reject malformed private handoff records before native guest publication."""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_handoff_state import BASE


def word(data,at):return struct.unpack_from('<I',data,at)[0]
def put(data,at,value):struct.pack_into('<I',data,at,value)


def sections(data):
    size=word(data,12);end=len(data)-32
    native,history,cache=struct.unpack_from('<3I',data,end+8)
    assert size==768 and size+native+history+cache+32==len(data)
    return size,size+native,history,size+native+history,cache


def seal(data):
    _,hist,hs,cache,cs=sections(data)
    for at,size,offset in ((hist,hs,48),(cache,cs,48),(0,len(data),56)):
        data[at+offset:at+offset+32]=bytes(32)
        data[at+offset:at+offset+32]=hashlib.sha256(data[at:at+size]).digest()
    return data


def main():
    out=BASE/'rejections';out.mkdir(exist_ok=True)
    build_path=BASE/'build-report.json';build=json.loads(build_path.read_text())
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    seed=BASE/'pilot-ready-final';seed_report=json.loads((seed/'report.json').read_text())
    binary=BASE/'handoff-state-probe.exe'
    assert digest(binary)==seed_report['binary_sha256']==build['runs']['probe']['binary_sha256']
    original=(seed/'revival.private-state').read_bytes();native,hist,hs,cache,cs=sections(original)
    fields=re.findall(r'X\((\w+),[^)]+\)',(ROOT/'tools/pride_handoff_state_context.c').read_text().split('#define STATE_ENUM')[0])
    offsets={name:224+i*4 for i,name in enumerate(fields)}
    def changed(at,value):
        data=bytearray(original);put(data,at,value);return seal(data)
    fixtures={'valid':original,'truncated':original[:-1],
        'bad-magic':b'INVALID!'+original[8:],
        'context-version':changed(8,2),'context-build':changed(24,word(original,24)^1),
        'context-reserved':changed(764,1),'context-ended':changed(offsets['owner_ended'],0),
        'context-normal-mark':changed(offsets['owner_normal_latch_serial'],word(original,offsets['owner_normal_latch_serial'])+1),
        'context-grounding':changed(offsets['grounded_done'],0),
        'context-spawn-x':changed(offsets['spawn_selected_x'],66),
        'context-spawn-source':changed(offsets['spawn_md'],0),
        'history-version':changed(hist+8,2),'history-field':changed(hist+96,2331),
        'history-age':changed(hist+100,300),'history-health-age':changed(hist+104,270),
        'history-ready-age':changed(hist+108,345),'history-normal-started':changed(hist+112,0),
        'history-normal-mark':changed(hist+116,word(original,hist+116)+1),
        'history-native-mark':changed(hist+120,word(original,hist+120)+1),
        'history-source-flags':changed(hist+80,word(original,hist+80)^1),
        'cache-version':changed(cache+8,2),'cache-field':changed(cache+80,2331),
        'cache-bank-length':changed(cache+88,word(original,cache+88)+1)}
    view_at=native+36+struct.unpack_from('<Q',original,native+24)[0]+4
    assert original[view_at:view_at+8]==b'TLKVIEW1'
    fixtures['native-view-mark']=changed(view_at+20,word(original,view_at+20)+1)
    results={}
    for name,data in fixtures.items():
        folder=out/name;folder.mkdir(exist_ok=True);state=folder/'fixture.state';state.write_bytes(data)
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',seed/'resources.ini','--frames','2340','--input-polled',seed/'resume.tape',
            '--load',state,'--wide','320']
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        assert run.returncode==(0 if name=='valid' else 8),(name,run.returncode)
        assert not list(folder.glob('*.part')),(name,'temporary file remains')
        results[name]=dict(exit_code=run.returncode,fixture_sha256=digest(state),log_sha256=digest(folder/'run.log'))
        print(name,run.returncode,flush=True)
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,ROOT/'tools/pride_handoff_state_context.c',seed/'revival.private-state',
        seed/'resources.ini',seed/'resume.tape')}
    report=dict(result='PASS',cases=results,source_sha256=sources,binary_sha256=digest(binary),
        rejection_scope='New-process structural, semantic and cross-section preflight; not complete same-process rollback.',
        full_first_level_fidelity_complete=False)
    (BASE/'rejections.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(results)-1,'rejections and one valid control PASS',flush=True)


if __name__=='__main__':main()
