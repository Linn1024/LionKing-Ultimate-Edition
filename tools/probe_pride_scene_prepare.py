"""Verify original Pride decoder ABI and isolated prepared-body reload experiments."""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',nargs='+',choices=('native','both'),default=['native','both'])
    parser.add_argument('--modes',nargs='+',choices=('control','prepared','scene','combined'),default=['control','prepared','scene','combined'])
    parser.add_argument('--reuse',action='store_true',help='Reanalyse completed captures from this exact research executable')
    args=parser.parse_args();out=ROOT/'build/pride-scene-prepare';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    binary=ROOT/'engine/build-win/tlk_scene_prepare_probe.exe';binary_hash=digest(binary)
    ref_path=ROOT/'build/pride-native-bank/report.json';ref=json.loads(ref_path.read_text());assert ref['result']=='PASS'
    spec=importlib.util.spec_from_file_location('scene_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    rom=(ROOT/'Lion King, The (USA).sfc').read_bytes()
    results={}
    for source in args.sources:
        for mode in args.modes:
            case=source+'-'+mode;folder=out/case;folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_NATIVE_BANK_PROBE']=env['TLK_SCENE_PREPARE_PROBE']=str(folder)
            env['TLK_NATIVE_BANK_APPLY']=str(int(mode in ('prepared','combined')));env.pop('TLK_NATIVE_BANK_RECORD',None)
            env['TLK_SCENE_PREPARE_APPLY']=str(int(mode in ('scene','combined')))
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini','--lle','--frames','5400',
                '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                '--ram-log',folder/'route.ram','--dump-png',folder/'picture.png']
            identity=folder/'capture-identity.json'
            if args.reuse:
                assert json.loads(identity.read_text())=={'binary_sha256':binary_hash},case
            else:
                identity.unlink(missing_ok=True)
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
                identity.write_text(json.dumps({'binary_sha256':binary_hash})+'\n')
            if mode in ('control','prepared'):
                old=ROOT/'build/pride-native-bank'/case
                assert hashes(folder/'run.log')==hashes(old/'run.log'),case
                assert digest(folder/'route.ram')==digest(old/'route.ram'),(case,'Observer changed tracked RAM')
            rows=list(csv.DictReader((folder/'decompress.csv').open()));calls={}
            for row in rows:calls.setdefault(row['call'],{})[row['event']]=row
            decoded=[]
            for number,events in calls.items():
                assert set(events) in ({'entry','loop','exit','return'},{'entry','loop','prepared','exit','return'}),(case,number,events.keys())
                entry,loop,exit,ret=(events[key] for key in ('entry','loop','exit','return'))
                src=int(entry['source'],16);dest=int(entry['destination'],16)
                assert 0xc00000<=src<0xf00000 and 0x7e0000<=dest<=0x7fffff,(case,number,src,dest)
                payload,used=lz.decompress(rom,src);at=dest-0x7e0000
                assert at+len(payload)<=0x20000
                before=(folder/(f'{int(number):03}-loop-wram.bin')).read_bytes()
                after=(folder/(f'{int(number):03}-exit-wram.bin')).read_bytes()
                assert after[at:at+len(payload)]==payload,(case,number,'Original decoder bytes differ')
                # Publish the actual write set, including scratch/NMI writes,
                # rather than assuming output bytes are the entire ABI.
                changed=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
                outside=[i for i in changed if not at<=i<at+len(payload)]
                assert int(ret['stack'],16)==(int(entry['stack'],16)+3)&65535,(case,number,'Long return stack')
                assert all(entry[key]==ret[key] for key in ('db','direct_page','m','x')),(case,number,'Return ABI')
                decoded.append({'call':int(number),'source':hex(src),'destination':hex(dest),
                    'prepared_body_applied':'prepared' in events,
                    'death_reload':bool(int(entry['death'])),'compressed_bytes':used,'decoded_bytes':len(payload),
                    'decoded_sha256':hashlib.sha256(payload).hexdigest(),
                    'entry_field':int(entry['field']),'return_field':int(ret['field']),
                    'decoder_fields':int(ret['field'])-int(entry['field']),
                    'outside_output_changed_addresses':outside,'entry':entry,'loop':loop,'exit':exit,'return':ret,
                    'terminal_dma1_sha256':digest(folder/(f'{int(number):03}-exit-dma1.bin'))})
            results[case]={'guest':hashes(folder/'run.log'),'calls':decoded,
                'tracked_ram_sha256':digest(folder/'route.ram'),'events_sha256':digest(folder/'decompress.csv'),
                'log_sha256':digest(folder/'run.log'),'picture_sha256':digest(folder/'picture.png'),
                'snapshots_sha256':{p.name:digest(p) for p in sorted(folder.glob('*.bin'))}}
            death=[r for r in decoded if r['death_reload']]
            prepared=[r for r in death if r['prepared_body_applied']]
            if mode in ('scene','combined'):
                assert len(prepared)==7 and all(r['decoder_fields']==0 for r in prepared),(case,'Prepared decoder readiness')
            else:assert not prepared
            points=list(csv.DictReader((folder/'events.csv').open()))
            marks={r['pc']:int(r['field']) for r in points if r['event']=='point'}
            results[case]['normal_age']=marks['c32b24']-marks['c089b7']
            print(case,len(decoded),'decoder calls,',sum(r['decoder_fields'] for r in death),'reload decoder fields, normal age',results[case]['normal_age'],
                'source bytes/ABI PASS' if prepared else 'exact reference guest/RAM PASS',flush=True)
    spans=[(0x10000,16000),(0x18800,0x2780),(0x1ba00,0x1d80),(0x1d780,0x880),(0x1e000,0xf00)]
    for source in args.sources:
        if source+'-control' not in results:continue
        baseline=results[source+'-control'];before={}
        for c in baseline['calls']:before[(c['source'],c['destination'])]=c
        for mode in ('scene','combined'):
            if source+'-'+mode not in results:continue
            case=source+'-'+mode;run=results[case]
            for c in run['calls']:
                if not c['prepared_body_applied']:continue
                original=before[c['source'],c['destination']]
                for key in ('a','rx','ry','p','db','m','x','direct_page','wram_port'):
                    assert c['exit'][key]==original['exit'][key],(case,c['source'],key)
                assert c['terminal_dma1_sha256']==original['terminal_dma1_sha256']
            a=(out/(source+'-control')/'normal-wram.bin').read_bytes();b=(out/case/'normal-wram.bin').read_bytes()
            assert all(a[p:p+n]==b[p:p+n] for p,n in spans),(case,'Restored scene data differs')
            run['normal_restored_map_and_npc_regions_match_original']=True
    assert digest(binary)==binary_hash
    report.write_text(json.dumps({'result':'PREPARED_DECODER_BODY_AND_NATIVE_ABI_VERIFIED_RUNTIME_OPEN','scope':__doc__,
        'capture_action':'reanalysed_existing_same_binary' if args.reuse else 'fresh_replay',
        'sources':args.sources,'modes':args.modes,'research_host_sha256':binary_hash,'runs':results,'production_decoder_bypass_enabled':False,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),ref_path,
            ROOT/'tools/pride_scene_prepare_probe.c',ROOT/'tools/pride_scene_template.h',ROOT/'tools/pride_native_bank_probe.c',ROOT/'engine/CMakeLists.txt',
            ROOT/'engine/tools/re/decompress.py',ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md',
            ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
            ROOT/'build/pride-death-phases/native.ini',ROOT/'build/pride-death-phases/both.ini')}},indent=2)+'\n')


if __name__=='__main__':main()
