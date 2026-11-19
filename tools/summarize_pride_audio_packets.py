"""Verify observed semantic caller -> CPU queue -> SPC slot -> physical voice."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT, read_rom
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def rows(path):
    with path.open() as stream:return list(csv.DictReader(stream))


def main():
    base=ROOT/'build/pride-lizard-launch-work/player'
    path=base/'audio-packet-audit2/report.json'
    assert all(bound(path)['checks'].values())
    previous=base/'audio-queue-owner-audit2/report.json'
    assert all(bound(previous)['checks'].values())
    rom=read_rom('Lion King, The (USA).sfc',
        '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    assert rom[0x2212e:0x22133]==bytes.fromhex('b56f8d4021')
    results={}
    for name in ('native','bounce'):
        folder=path.parent/name
        queue=rows(folder/'queue.csv')
        assert queue==rows(previous.parent/name/'queue.csv')
        transfer=rows(folder/'transfer.csv');spc=rows(folder/'spc.csv')
        requests=[r for r in queue if r['command']=='8011'];assert len(requests)==6
        consumed=[i for i,r in enumerate(spc) if r['pc']=='1bcb' and r['param8']=='11']
        assert len(consumed)==6
        chains=[]
        for request,index in zip(requests,consumed):
            field=int(request['field']);cursor=int(request['cursor'])
            words=[r for r in transfer if int(r['field'])==field]
            start=[i for i,r in enumerate(words) if int(r['source_cursor'])==cursor]
            assert len(start)==1
            words=words[start[0]:start[0]+4]
            assert [int(r['source_cursor']) for r in words]==list(range(cursor,cursor+8,2))
            volume='0078' if name=='native' else '0000'
            assert [r['word'] for r in words]==['1102','0000','8003',volume]
            destination=int(words[0]['destination'],16)
            assert 0x204<=destination<0x244
            assert [int(r['destination'],16) for r in words]==[
                0x204+((destination-0x204+i)&63) for i in range(0,8,2)]
            chain=spc[index:index+5]
            assert [r['pc'] for r in chain]==['1bcb','1be3','113d','0fd1','0d34']
            assert all(int(r['field'])==field for r in chain)
            assert int(chain[0]['y'],16)==destination-0x204
            assert int(chain[0]['ring_cursor'],16)==(destination-0x204+4)&63
            assert chain[0]['code']=='f604021c5d3f9905'
            assert chain[1]['code']=='ebebf60502c57802' and chain[1]['x']=='04'
            assert chain[3]['x']=='08' and chain[4]['a']=='08'
            assert chain[3]['lookup']==('440d' if field>3900 else '3d15')
            assert int(chain[4]['x'],16)<8
            assert request['caller_return']=='c36686'
            chains.append(dict(field=field,caller='c36686',cpu_cursor=cursor,
                spc_destination=f'{destination:04x}',program=17,software_slot=8,
                script=chain[3]['lookup'],physical_voice=int(chain[4]['x'],16)))
        results[name]=dict(accepted_requests=len(queue),transferred_words=len(transfer),
            spc_observations=len(spc),verified_bounce_chains=chains,
            observer_neutral_full_guest_fields=4500)
    sources=[Path(__file__),path,previous,ROOT/'tools/native_spc_packet_trace2.h',
        ROOT/'tools/native_audio_packet_observer2.c']
    output=ROOT/'build/pride-lizard-launch-work/native-packet-chain-report.json'
    assert not output.exists()
    report=dict(result='OBSERVED_NATIVE_CALLER_TO_PHYSICAL_VOICE_VERIFIED',
        observations=results,semantic_tags_implemented=False,
        all_queue_rejection_and_reset_paths_verified=False,
        production_changed=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources})
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],{n:len(r['verified_bounce_chains']) for n,r in results.items()},flush=True)


if __name__=='__main__':main()
