"""Observe original native reload and verify prepared-bank bytes in isolated experiments.

The control is read-only and must match the ordinary original route exactly.
Experiments test the native fast flag, alternate queue service, bounded batching
and a bank template captured during ordinary initialization. These deliberately
change guest state and are not shipped gameplay or full audio-fidelity proof.
No distributed host is changed.
"""
import csv
import argparse
import hashlib
import json
import os
import struct
import importlib.util
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reuse',action='store_true')
    parser.add_argument('--sources',nargs='+',choices=('native','both'),default=['native','both'])
    parser.add_argument('--experiments',nargs='+',choices=('fast','drain','batch','cached'),default=['fast','drain','batch','cached'])
    args=parser.parse_args()
    out=ROOT/'build/pride-native-reload-owner';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    identities={p:digest(ROOT/p) for p in ('dist/LionKing.exe','engine/build-win/tlk_headless.exe')}
    earlier_path=ROOT/'build/pride-death-phases/report.json';earlier=json.loads(earlier_path.read_text())
    assert earlier['result']=='PASS' and earlier['headless_sha256']==identities['engine/build-win/tlk_headless.exe']
    results={};runs={}
    for source in args.sources:
        for mode in ['control',*args.experiments]:
            fast=mode=='fast';name=source+'-'+mode;folder=out/name;folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_RELOAD_PROBE']=str(folder);env['TLK_RELOAD_FAST_SAMPLES']=str(int(fast))
            env['TLK_RELOAD_DRAIN_SAMPLES']=str(int(mode=='drain'))
            env['TLK_RELOAD_BATCH_SAMPLES']=str(int(mode=='batch'))
            env['TLK_RELOAD_CACHED_BANK']=str(int(mode=='cached'))
            cmd=[ROOT/'engine/build-win/tlk_pride_reload_probe.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini',
                '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape','--frames','5400',
                '--lle','--ram-log',folder/'route.ram','--dump-png',folder/'picture.png']
            log_path=folder/'run.log'
            reuse=args.reuse and log_path.exists() and log_path.stat().st_mtime_ns>=(ROOT/'engine/build-win/tlk_pride_reload_probe.exe').stat().st_mtime_ns
            if not reuse:
                with log_path.open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            assert 'result=completed frames=5400' in log_path.read_text()
            assert len((folder/'route.ram').read_text().splitlines())==5400
            events=list(csv.DictReader((folder/'events.csv').open()));assert events and {r['episode'] for r in events}=={'1'}
            assert 'cached_restores' in events[0]
            points={pc:[r for r in events if r['pc']==pc] for pc in {r['pc'] for r in events}}
            one=lambda pc:points[pc][0] if len(points.get(pc,[]))==1 else None
            if mode=='drain' and one('c082bb') is None:
                assert one('c082a5') and int(events[-1]['drain_calls'])>0 and events[-1]['fast_writes']=='0'
                fields=list(csv.DictReader((folder/'fields.csv').open()))
                assert int(fields[-1]['frame'])==5200 and fields[-1]['phase']=='2'
                results[name]={'outcome':'BANK_NOT_READY_WITHIN_5400_FIELDS','bank_start_host_field':int(one('c082a5')['host_field']),
                    'drain_calls':int(events[-1]['drain_calls']),'sample_bank_return_observed':False,'normal_play_entry_observed':False,
                    'guest':hashes(log_path),'complete_tracked_ram_sha256':digest(folder/'route.ram'),
                    'events_sha256':digest(folder/'events.csv'),'field_samples_sha256':digest(folder/'fields.csv'),
                    'run_log_sha256':digest(log_path),'picture_sha256':digest(folder/'picture.png')}
                print(name,'bank return/normal-play not observed within5400 fields; alternate call mode rejected',flush=True)
                continue
            for pc in ('c089b7','c08b05','c08b1f','c08122','c08131','c08135','c082a5','c082bb','c08650','c08859','c32b24'):
                assert one(pc) is not None,(name,pc)
            if mode=='control':
                assert hashes(folder/'run.log')==earlier['runs'][source]['guest']
                assert digest(folder/'route.ram')==earlier['runs'][source]['tracked_sha256']
                assert all(r['fast_writes']=='0' for r in events)
            elif fast:
                assert events[-1]['fast_writes']==events[-1]['fast_restores']=='1' and one('c082bb')['fast_flag']=='0'
            elif mode=='drain':
                assert events[-1]['fast_writes']=='0' and int(events[-1]['drain_calls'])>0
            elif mode=='batch':
                assert events[-1]['fast_writes']=='0' and int(events[-1]['batch_services'])>0 and int(events[-1]['batch_skips'])>0
            else:
                assert events[-1]['cached_restores']=='1' and events[-1]['fast_writes']=='0'
                assert 0<int(events[-1]['template_field'])<int(one('c089b7')['host_field'])
            start=int(one('c089b7')['host_field'])
            result={'opcode_event_count':len(events),'guest':hashes(folder/'run.log'),
                'points':{pc:{'host_field':int(one(pc)['host_field']),'relative_field':int(one(pc)['host_field'])-start,
                              'opcode_field':int(one(pc)['opcode_field']),'stack':one(pc)['stack'],
                              'db':one(pc)['db'],'direct_page':one(pc)['direct_page']}
                    for pc in ('c089b7','c08b05','c08b1f','c08122','c08131','c08135','c082a5','c082bb','c08650','c08859','c32b24')},
                'sample_bank_host_fields':int(one('c082bb')['host_field'])-int(one('c082a5')['host_field']),
                'complete_tracked_ram_sha256':digest(folder/'route.ram'),
                'events_sha256':digest(folder/'events.csv'),'field_samples_sha256':digest(folder/'fields.csv'),
                'run_log_sha256':digest(log_path),'picture_sha256':digest(folder/'picture.png'),
                'template_capture_field':int(events[-1]['template_field']),
                'template_files_sha256':{p.name:digest(p) for p in sorted(folder.glob('template-*'))},
                'snapshots_sha256':{p.name:digest(p) for p in sorted(folder.glob('1-*.bin'))}}
            runs[name]=(folder,events,result);results[name]=result
            print(name,'native normal-play entry observed at age',result['points']['c32b24']['relative_field'],
                  'sample-bank span',result['sample_bank_host_fields'],flush=True)
        def transfers(events):
            start=next(int(r['host_field']) for r in events if r['pc']=='c082a5')
            stop=next(int(r['host_field']) for r in events if r['pc']=='c082bb')
            return [(r['pc'],r['a'],r['rx'],r['ry']) for r in events if r['pc'] in ('c21906','c21909','c2191e') and start<=int(r['host_field'])<=stop]
        control,ce,cr=runs[source+'-control']
        rom=(ROOT/'Lion King, The (USA).sfc').read_bytes()
        original_transfers=transfers(ce)
        blocks=[]
        for pc,bank,_,address in original_transfers:
            if pc!='c21909':continue
            at=(((int(bank,16)&255)<<16)|int(address,16))&0x3fffff
            size=struct.unpack_from('<H',rom,at)[0];assert size and at+size<=len(rom)
            blocks.append((at,rom[at:at+size]))
        assert len(blocks)==20 and sum(len(data) for _,data in blocks)==43560
        end=int.from_bytes((control/'1-after-bank-wram.bin').read_bytes()[0x1fce:0x1fd0],'little')
        offset=end-sum(len(data) for _,data in blocks);assert offset==0x3e48
        original_aram=(control/'1-after-bank-aram.bin').read_bytes()
        spec=importlib.util.spec_from_file_location('native_reload_lz',ROOT/'engine/tools/re/decompress.py')
        lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
        score_source=int.from_bytes(rom[0x223cf+12*3:0x223d2+12*3],'little')
        score,_=lz.decompress(rom,score_source);assert len(score)==6250
        assert original_aram[0x25de:0x25de+len(score)]==score
        for _,data in blocks:
            assert original_aram[offset:offset+len(data)]==data
            offset+=len(data)
        at=end-sum(len(data) for _,data in blocks)
        for _,data in blocks:
            expected=struct.pack('<HH',at+3+int.from_bytes(data[4:6],'little'),at+3+int.from_bytes(data[6:8],'little'))
            assert original_aram[0x2300+data[3]*4:0x2304+data[3]*4]==expected
            at+=len(data)
        cr['original_sample_blocks']=20;cr['original_sample_bytes']=43560
        cr['original_score_bytes']=6250
        for mode in args.experiments:
            if 'points' not in results[source+'-'+mode]:continue
            fast,fe,fr=runs[source+'-'+mode]
            for label in ('death-entry-wram','before-bank-wram','before-bank-aram'):
                assert (control/f'1-{label}.bin').read_bytes()==(fast/f'1-{label}.bin').read_bytes(),(source,label)
            if mode=='cached':assert not transfers(fe)
            else:assert transfers(ce)==transfers(fe),'Experiment changed submitted original upload arguments'
            after_control=(control/'1-after-bank-aram.bin').read_bytes();after_fast=(fast/'1-after-bank-aram.bin').read_bytes()
            differences=[i for i,(a,b) in enumerate(zip(after_control,after_fast)) if a!=b]
            offset=end-sum(len(data) for _,data in blocks);matched=[]
            for number,(_,data) in enumerate(blocks):
                if after_fast[offset:offset+len(data)]==data:matched.append(number)
                offset+=len(data)
            if mode=='cached':
                assert matched==list(range(20)) and after_control[0x2400:end]==after_fast[0x2400:end]
                assert fr['sample_bank_host_fields']==0
                template=(fast/'template-aram.bin').read_bytes()
                metadata=json.loads((fast/'template-metadata.json').read_text())
                assert metadata['directory_entries']==20 and metadata['port_queue']==metadata['driver_flags']==0
                assert template[0x25de:0x25de+6250]==score
                template=bytearray(template);before=(fast/'1-before-bank-aram.bin').read_bytes()
                ids={rom[at+3] for at,_ in blocks}
                for i in range(178):
                    if i not in ids:template[0x2300+i*4:0x2304+i*4]=before[0x2300+i*4:0x2304+i*4]
                assert template[0x2400:end]==after_control[0x2400:end]
            if mode=='fast':assert matched==list(range(14,20))
            if mode=='batch':assert matched==list(range(20)) and after_control[0x2400:end]==after_fast[0x2400:end]
            normal_control=(control/'1-normal-state-aram.bin').read_bytes();normal_fast=(fast/'1-normal-state-aram.bin').read_bytes()
            a=(control/'1-normal-state-wram.bin').read_bytes();b=(fast/'1-normal-state-wram.bin').read_bytes()
            ca=(control/'1-after-bank-wram.bin').read_bytes();fa=(fast/'1-after-bank-wram.bin').read_bytes()
            end=int.from_bytes(ca[0x1fce:0x1fd0],'little')
            assert 0x2400<end<=0xffff and fa[0x1fce:0x1fd0]==ca[0x1fce:0x1fd0]
            spans=[(0x10000,16000),(0x18800,0x3200),(0x1ba00,0x1d80),(0x1d780,0x880),(0x1e000,0x2000)]
            assert all(a[p:p+n]==b[p:p+n] for p,n in spans),source
            results[source+'-'+mode]['transfer_commands']=transfers(fe)
            results[source+'-'+mode]['comparison']={'unchanged_before_sample_bank':True,'identical_original_transfer_arguments':mode!='cached',
                'original_transfer_work_replaced_by_prepared_bank':mode=='cached',
                'same_restored_level_map_and_graphics':True,'aram_different_bytes':len(differences),
                'aram_difference_address_range':[min(differences),max(differences)] if differences else [],
                'aram_bytes_equal_from_2400':after_control[0x2400:]==after_fast[0x2400:],
                'normal_aram_different_bytes':sum(a!=b for a,b in zip(normal_control,normal_fast)),
                'sample_arena_end':end,'sample_arena_matches_at_return':after_control[0x2400:end]==after_fast[0x2400:end],
                'sample_arena_matches_at_normal_play':normal_control[0x2400:end]==normal_fast[0x2400:end],
                'source_named_directory_entries':sorted({rom[at+3] for at,_ in blocks}),
                'original_sample_blocks_matched':matched,'original_sample_block_count':20,'original_sample_bytes':43560,
                'restored_wram_regions':[{'offset':p,'bytes':n} for p,n in spans],
                'original_score_bytes':6250,'original_score_exact_at_return':after_fast[0x25de:0x25de+6250]==score,
                'normal_entry_fields_saved':cr['points']['c32b24']['relative_field']-fr['points']['c32b24']['relative_field']}
    assert all(digest(ROOT/p)==sha for p,sha in identities.items())
    result={'result':'NATIVE_RELOAD_OWNERSHIP_AND_BANK_BYTES_VERIFIED_RUNTIME_OPEN','scope':__doc__,
        'player_sha256':identities['dist/LionKing.exe'],'headless_sha256':identities['engine/build-win/tlk_headless.exe'],
        'research_host_sha256':digest(ROOT/'engine/build-win/tlk_pride_reload_probe.exe'),'runs':results,
        'original_controls_unchanged':True,'experimental_guest_flag_write':True,'production_death_gameplay_enabled':False,
        'shorter_reload_does_not_prove_audio_ready':True,
        'sources':args.sources,'experiments':args.experiments,'execution_mode':'LLE only',
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
            Path(__file__),ROOT/'tools/pride_reload_probe.c',ROOT/'engine/runner/headless_main.c',ROOT/'engine/CMakeLists.txt',
            ROOT/'tools/pride_audio_bank_template.h',
            ROOT/'engine/tools/re/decompress.py',ROOT/'engine/snesrecomp/runner/src/snes/apu.c',
            ROOT/'engine/snesrecomp/runner/src/snes/dsp.c',ROOT/'engine/snesrecomp/runner/src/snes/spc.c',
            ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md',
            earlier_path,ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
            ROOT/'build/pride-death-phases/native.ini',ROOT/'build/pride-death-phases/both.ini')}}
    report.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
