"""Verify the first shared ledge's original sound difference without enabling it."""
import csv
import json
from pathlib import Path
import struct

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arrival_history import bound


def main():
    out=ROOT/'build/pride-ledge-grab-audio';out.mkdir()
    md_path=ROOT/'build/pride-cub-contact-audio/report.json';md=bound(md_path)
    census_path=ROOT/'build/pride-audio-inventory/report.json';census=bound(census_path)
    native_path=ROOT/'build/native-pickup-flight2/report.json';bound(native_path)
    events_path=ROOT/'build/pride-pickup-arrival-audio/report.json';bound(events_path)
    assert md['result']=='ORIGINAL_CONTACT_AUDIO_ENTRIES_CAPTURED'
    assert census['result']=='ORIGINAL_PRIDE_CENSUS_CAPTURED'
    entries=md['entries'];assert [int(r['field']) for r in entries]==[1874,2703,4191]
    commands=list(csv.DictReader((census_path.parent/'commands.csv').open()))
    sounds=[r for r in commands if r['level']=='1' and r['selector']=='2' and r['value']=='94'
            and r['outer_caller'] in ('195fb8','1961e8')]
    assert [int(r['frame']) for r in sounds]==[1874,2703,4191]
    for entry,sound in zip(entries,sounds):
        assert entry['action']==sound['actor_state'] and entry['actor']==sound['actor']
    groups=[]
    for field in range(900,4001,4):
        ram=(ROOT/f'build/native-pickup-flight/hl_wram_{field}.bin').read_bytes()
        word=lambda at:struct.unpack_from('<H',ram,at)[0]
        address=lambda at:int.from_bytes(ram[at:at+3],'little')
        if word(0x1ff9e) or address(0xdf) not in (0xc00387,0xc0080d):continue
        action=address(0xb243)
        if action not in (0xc33d1f,0xc33f11):continue
        row=dict(field=field,action=f'{action:06x}',x=word(0xb21b),y=word(0xb21d),timer=word(0xb23f))
        if not groups or field>groups[-1][-1]['field']+4 or groups[-1][-1]['action']!=row['action']:groups.append([])
        groups[-1].append(row)
    first=groups[0];assert first[0]==dict(field=1472,action='c33d1f',x=543,y=785,timer=42)
    assert first[-1]['field']==1516 and first[-1]['timer']==0
    native_events=list(csv.DictReader((events_path.parent/'native-events.csv').open()))
    near=[r for r in native_events if int(r['actor'],16)==0xb213
          and first[0]['field']-8<=int(r['frame'])<=first[-1]['field']+8]
    assert not near
    counterpart=next(r for r in md['observations'] if r['field']==1874)
    assert (counterpart['action'],counterpart['x'],counterpart['y'],counterpart['timer'])==('194b94',543,785,42)
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    for at in (0x195fae,0x1961de):assert rom[at:at+10]==bytes.fromhex('3f3c005e4eb90000228a')
    paths=[Path(__file__),md_path,census_path,native_path,events_path,ROOT/'tools/pride_arrival_history.py']
    report=dict(result='ORIGINAL_FIRST_SHARED_LEDGE_SOUND_DIFFERENCE_VERIFIED',
        md_contact_entries=entries,md_sound_calls=sounds,native_first_ledge_samples=first,
        md_first_ledge=counterpart,native_sound_calls_in_enclosing_first_ledge_window=0,
        shared_first_position=[543,785],shared_initial_timer=42,
        original_md_contact_helpers=['195FA6','1961D6'],original_native_contact_helpers=['C351A8','C3537A'],
        opposite_direction_native_lifetime_verified=False,all_contact_branches_verified=False,
        gameplay_timing_equivalence_proven=False,production_mapping_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'first shared ledge543/785 timer42: MD FM94, native silent',flush=True)


if __name__=='__main__':main()
