"""Bind native cue17 to original SPC program, software owner and DSP writes."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player'
    writer=base/'spc-owner-audit/report.json';assert all(bound(writer)['checks'].values())
    voices=base/'spc-voice-owner-audit/report.json';assert all(bound(voices)['checks'].values())
    with (writer.parent/'native/spc-writes.csv').open() as stream:writes=list(csv.DictReader(stream))
    ram=(writer.parent/'native/aram_1400.bin').read_bytes()
    assert ram[0x0d34:0x0d37]==bytes.fromhex('d52705')
    assert ram[0x0e0f:0x0e15]==bytes.fromhex('cef71fd5f902')
    assert ram[0x061f:0x0627]==bytes.fromhex('8502f6001ec58602')
    assert int.from_bytes(ram[0xcae:0xcb0],'little')==0xe0f # E6 dispatch slot
    pairs=[]
    for channel in (7,5):
        owner_write=next(r for r in writes if r['pc']=='0d34' and int(r['at'],16)==0x527+channel)
        slot=int(owner_write['value'],16);assert slot<22
        patch=next(r for r in writes if r['pc']=='0e12' and int(r['at'],16)==0x2f9+slot and int(r['value'],16)==0x3e)
        actual=next(r for r in writes if r['at']=='00f3' and int(r['dsp_reg'],16)==channel*16+4 and r['value']=='5c')
        pairs.append(dict(channel=channel,software_slot=slot,patch=int(patch['value'],16),
            dsp_source=int(actual['value'],16),assignment_field=int(owner_write['field']),dsp_field=int(actual['field'])))
    assert ram[0x1e00+0x3e]==92
    assert [i for i in range(128) if ram[0x1e00+i]==92]==[0x3e]
    # Original lookup output captured after its execution; compare the header.
    start=ram[0x294]|ram[0x295]<<8;header=start-15
    assert ram[header+2]==17 and ram[header+3]==1
    assert ram[start+4:start+6]==bytes.fromhex('e63e')
    for name in ('native','bounce'):
        for snapshot in (writer.parent/name).glob('aram_*.bin'):
            assert snapshot.read_bytes()==(base/'bounce-dsp-audit'/name/snapshot.name).read_bytes()
    with (voices.parent/'native/dsp.csv').open() as stream:
        live=[r for r in csv.DictReader(stream) if r['level']=='0' and r['scene'] in ('c00387','c0080d')
            and r['srcn']=='92' and int(r['gain']) and int(r['sample']) and (int(r['volume_l']) or int(r['volume_r']))]
    assert len(live)==143
    assert all(int(r['program11_start'],16)<=int(r['base'],16)<int(r['program11_end'],16) for r in live)
    banks=sorted({(r['program11_start'],r['program11_end'],r['roots']) for r in live})
    assert len(banks)==2
    paths=[Path(__file__),writer,voices,ROOT/'tools/native_spc_owner_trace.h']
    report=dict(result='OBSERVED_NATIVE_BOUNCE_OWNERSHIP_CHAIN_VERIFIED',first_two_assignments=pairs,
        original_lookup_stream=f'{start:04x}',original_header=f'{header:04x}',native_program_id=17,
        source_patch=62,dsp_source=92,read_only_aram_snapshots_exact=16,
        live_field_snapshots_with_program11_owner=143,observed_banks=banks,
        all_dsp_samples_or_unobserved_contexts_proven=False,
        production_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=ROOT/'build/pride-lizard-launch-work/spc-owner-chain-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n');print(report['result'],pairs,'banks',banks,flush=True)


if __name__=='__main__':main()
