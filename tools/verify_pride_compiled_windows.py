"""Compare real Windows clients and guest state for the private compiled bridge.

This covers the native presenter only, not prepared scene graphics or lifecycle.
"""
import csv
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def saved_wram(path,expected,known_offset=None):
    data=path.read_bytes();assert data[:8]==b'TLKSTAT1'
    assert struct.unpack_from('<I',data,8)[0]==4
    length=struct.unpack_from('<Q',data,24)[0];blob=data[36:36+length]
    # Existing decoder telemetry supplies search needles, not an equality
    # oracle. Accept an offset only after verifying all128KiB against the
    # independent endpoint hash; game execution chunks may follow SNES RAM.
    candidates=[] if known_offset is None else [known_offset]
    reference=(path.parent/'capture-wram.bin').read_bytes()
    for offset in range(0,len(reference)-256,256):
        needle=reference[offset:offset+256]
        if len(set(needle))<32:continue
        start=0
        while (start:=blob.find(needle,start))>=0:
            at=start-offset
            if 0<=at<=len(blob)-0x20000:candidates.append(at)
            start+=1
    for at in dict.fromkeys(candidates):
        ram=blob[at:at+0x20000]
        if hashlib.sha256(ram).hexdigest()==expected:return ram,at
    raise AssertionError('full WRAM hash not found using captured RAM needles')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,default=Path('build/pride-compiled-revival/windows'))
    parser.add_argument('--width',type=int,choices=(256,320),default=256)
    args=parser.parse_args();width=args.width
    base=ROOT/'build/pride-compiled-revival';out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    (out/'report.json').write_text('{"result":"RUNNING"}\n')
    binary=base/'compiled-restore-sdl.exe';report=base/'sdl-build-report.json'
    build=json.loads(report.read_text());assert digest(binary)==build['binary_sha256']
    assert digest(base/'build-report.json')==build['headless_build_report_sha256']
    original=json.loads((base/'build-report.json').read_text())
    sources={name:sha for name,sha in original['source_sha256'].items()}
    sources[str(Path(__file__).relative_to(ROOT)).replace('\\','/')]=digest(Path(__file__))
    sources[str(report.relative_to(ROOT)).replace('\\','/')]=digest(report)
    for name,sha in sources.items():assert digest(ROOT/name)==sha,name
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
    results={}
    for phase,end in (('death',4500),('revival',4703),('ready',4775)):
        cases={}
        for mode in ('aot','lle'):
            folder=out/(phase+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):
                env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                        'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):env[key]='1'
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_WATCH',None)
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--config',config,'--resource-profile',profile,'--frames',end,'--no-pace','--no-audio','--no-record',
                 '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                 '--hash-at',end,'--save-at',end,folder/'snapshot.state',
                 '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
            if mode=='lle':cmd.append('--lle')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            stats=re.search(r'pride_compiled_hook_calls=(\d+) callbacks=(\d+) redirects=(\d+) paired_services=(\d+)',
                            (folder/'run.log').read_text(errors='replace'))
            assert stats and (int(stats[2])>0 if mode=='aot' else int(stats[1])==0)
            cases[mode]=dict(guest=hashes(folder/'run.log'),compiled_hook_statistics=list(map(int,stats.groups())),
                artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        a=out/(phase+'-aot');b=out/(phase+'-lle')
        assert cases['aot']['guest']['frame_sha256']==cases['lle']['guest']['frame_sha256']
        ar,ao=saved_wram(a/'snapshot.state',cases['aot']['guest']['wram_sha256'])
        br,bo=saved_wram(b/'snapshot.state',cases['lle']['guest']['wram_sha256'],ao)
        assert ao==bo
        differences=[dict(address=f'{n:05x}',aot=x,lle=y) for n,(x,y) in enumerate(zip(ar,br)) if x!=y]
        for name in ('owner-events.csv','restore-events.csv','owner-fields.csv','restore-fields.csv'):
            assert rows(a/name)==rows(b/name),name
        aw,ah,ap=pixels(a/'window.png');bw,bh,bp=pixels(b/'window.png')
        assert (aw,ah)==(bw,bh)==(width*2,448)
        assert ap==bp,'compiled and interpreter client pixels differ'
        assert len(set(ap))>1,'client is a single flat color'
        results[phase]=dict(runs=cases,guest_hashes_exact=cases['aot']['guest']==cases['lle']['guest'],
            full_wram_exact=not differences,full_wram_differences=differences,snapshot_wram_offset=ao,
            owner_and_restore_events_and_fields_exact=True,
            real_client_pixels_exact=aw*ah)
        print(phase+': native Windows clients and scene fields exact; WRAM differences='+str(len(differences)),flush=True)
    for name,sha in sources.items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['binary_sha256']
    (out/'report.json').write_text(json.dumps(dict(result='PASS' if all(v['full_wram_exact'] for v in results.values()) else 'AUDITED',scope=__doc__,runs=results,width=width,
        binary_sha256=digest(binary),source_sha256=sources,real_client_pixels_exact=sum(r['real_client_pixels_exact'] for r in results.values()),
        prepared_graphics_verified=False,production_behavior_enabled=False,full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
