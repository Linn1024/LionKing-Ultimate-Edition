"""Review the separate original lizard launch cue before implementing it."""
import csv
import json
from pathlib import Path
import struct

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_ledge_preview_history import bound


def main():
    md_path=ROOT/'build/pride-enemy-launch-audio/report.json';md=bound(md_path)
    native_path=ROOT/'build/native-pickup-flight2/report.json';bound(native_path)
    audio_path=ROOT/'build/native-ledge-audio/report.json';bound(audio_path)
    catalog_path=ROOT/'tools/pride_npc_pairs.json';catalog=json.loads(catalog_path.read_text())['pairs']
    lizard_native={int(r['snes'],16) for r in catalog if r['role']=='lizard'}
    lizard_md={int(r['md'],16) for r in catalog if r['role']=='lizard'}
    assert md['result']=='ORIGINAL_NPC_LAUNCH_SOUND_CAPTURED' and len(md['events'])==2
    assert all(r['descriptor']=='09793a' and r['action']=='199cc2' and r['timer']=='20'
               and int(r['pose'],16) in lizard_md for r in md['events'])
    observations=[]
    for field in range(900,4001,4):
        ram=(ROOT/f'build/native-pickup-flight/hl_wram_{field}.bin').read_bytes()
        word=lambda at:struct.unpack_from('<H',ram,at)[0]
        address=lambda at:int.from_bytes(ram[at:at+3],'little')
        if word(0x1ff9e) or address(0xdf) not in (0xc00387,0xc0080d):continue
        actor=word(0x76);previous=0;seen=set()
        while actor:
            assert 0x8000<=actor<=0xff80 and actor not in seen and word(actor)==previous
            seen.add(actor)
            if address(actor+0x30)==0xc15363:
                draw=word(actor+12);assert 0x8000<=draw<=0xffe0
                assert address(actor+4)==0xc58c50 and address(draw+10) in lizard_native
                observations.append(dict(field=field,actor=f'{actor:04x}',descriptor='c58c50',action='c15363',
                    timer=word(actor+0x2c),x=word(actor+8),y=word(actor+10),pose=f'{address(draw+10):06x}'))
            previous,actor=actor,word(actor+2)
    groups=[]
    for row in observations:
        if not groups or row['actor']!=groups[-1][-1]['actor'] or row['field']>groups[-1][-1]['field']+4:groups.append([])
        groups[-1].append(row)
    assert len(groups)==2
    audio=list(csv.DictReader((audio_path.parent/'allbugs/audio.csv').open()));intervals=[]
    for group in groups:
        start,end=group[0]['field']-4,group[-1]['field']+4;actor=group[0]['actor']
        related=[r for r in audio if r['actor']==actor and start<=int(r['frame'])<=end]
        assert not related,(group,related)
        intervals.append(dict(first_sample=group[0],last_sample=group[-1],enclosing_audio_fields=[start,end],
            native_actor_audio_calls=related))
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    external=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    assert snes[0x153ca:0x153cd]==bytes.fromhex('a9faff')
    assert snes[0x153e5:0x153e8]==bytes.fromhex('e91400')
    assert snes[0x153ea:0x153ed]==bytes.fromhex('a91400')
    assert snes[0x153f2:0x153f5]==bytes.fromhex('4cc254')
    assert external[0x199d0e:0x199d16]==bytes.fromhex('237cfffa0000003c')
    assert external[0x199d24:0x199d2a]==bytes.fromhex('337c0014002c')
    assert external[0x199d2a:0x199d34]==bytes.fromhex('3f3c007b4eb90000228a')
    out=ROOT/'build/pride-lizard-launch-audio';out.mkdir()
    paths=[Path(__file__),md_path,native_path,audio_path,catalog_path]
    report=dict(result='ORIGINAL_LIZARD_LAUNCH_SOUND_DIFFERENCE_VERIFIED',md_events=md['events'],native_intervals=intervals,
        initial_timer=20,initial_vy_q16=-6*65536,initial_y_subtraction=20,
        native_action='C15363',md_action='199CC2',md_only_command=[2,123],native_candidate_seam='C153F2',
        sparse_native_sampling_interval=4,exact_cross_console_field_or_movement_equivalence_proven=False,
        separate_from_simba_bounce_and_generic_defeat_puff=True,production_mapping_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'two actual launches; MD FM123, native actor silent in enclosing windows',flush=True)


if __name__=='__main__':main()
