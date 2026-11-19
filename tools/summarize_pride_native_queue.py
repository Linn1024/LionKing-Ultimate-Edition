"""Bind accepted caller identity to original queue instructions and observations."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT, read_rom
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player'
    report_path=base/'audio-queue-owner-audit2/report.json'
    report=bound(report_path)
    assert all(report['checks'].values())
    survey_path=base/'audio-queue-dispatch-audit/report.json'
    assert all(bound(survey_path)['checks'].values())
    rom=read_rom('Lion King, The (USA).sfc',
        '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    # Both lock rejection and capacity rejection precede this seam.
    assert rom[0x21c79:0x21c90]==bytes.fromhex(
        'e6bfd045851986158417e220a90285c7a66de04c00b02a')
    assert rom[0x21c90:0x21ca0]==bytes.fromhex('a5c7956fa5159570a5199571a5179572')
    assert rom[0x21ca0:0x21cb0]==bytes.fromhex('a9039573a5169574a5189575a51a9576')
    observations={}
    for name in ('native','bounce'):
        with (report_path.parent/name/'queue.csv').open() as stream:
            rows=list(csv.DictReader(stream))
        assert len(rows)==59
        bounce=[r for r in rows if r['command']=='8011']
        assert len(bounce)==6
        for row in bounce:
            stack=bytes.fromhex(row['stack_bytes'])
            assert int.from_bytes(stack[16:19],'little')+1==0xc36686
            assert row['caller_return']=='c36686'
            assert row['actor']=='b213' and row['descriptor']=='c5858a' and row['age']=='0'
            assert int(row['cursor'])==int(row['producer'])<0x4c
            assert row['parameter']==('7800' if name=='native' else '0000')
        with (survey_path.parent/name/'dispatch.csv').open() as stream:
            accepted=[r for r in csv.DictReader(stream) if r['pc']=='c21c90']
        assert len(accepted)==2
        assert all((r['d'],r['db'],r['m'],r['x'])==('1f00','7e','1','0') for r in accepted)
        observations[name]=dict(accepted_fx_requests=len(rows),bounce_requests=len(bounce),
            bounce_fields=[int(r['field']) for r in bounce],caller_return='c36686',
            full_guest_fields_observer_neutral=4500)
    paths=[Path(__file__),report_path,survey_path,
        ROOT/'tools/native_audio_queue_owner_observer2.c']
    output=ROOT/'build/pride-lizard-launch-work/native-queue-caller-report.json'
    assert not output.exists()
    result=dict(result='OBSERVED_ACCEPTED_NATIVE_QUEUE_CALLER_VERIFIED',
        original_accepted_seam='c21c90',required_m=1,required_x=0,
        native_packet_bytes=8,caller_stack_offset=17,observations=observations,
        semantic_tags_implemented=False,production_changed=False,
        full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],observations,flush=True)


if __name__=='__main__':main()
