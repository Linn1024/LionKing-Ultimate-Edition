"""Bound native program17 callers before broadening an output filter."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest


def offsets(data,pattern):
    found=[];start=0
    while True:
        at=data.find(pattern,start)
        if at<0:return found
        found.append(at);start=at+1


def main():
    rom_path=ROOT/'Lion King, The (USA).sfc'
    rom=read_rom(rom_path.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    pushes=offsets(rom,bytes.fromhex('f4110022ec2cc2'))
    assert pushes==[0x2e998,0x36362,0x3667f]
    returns=[at+0xc00000+7 for at in pushes]
    assert returns==[0xc2e99f,0xc36369,0xc36686]
    direct=offsets(rom,bytes.fromhex('22ec62c3'))
    assert direct==[0x30391,0x30834,0x30e47,0x30fce]
    for at in direct:
        gate=rom[at-8:at]
        assert gate[:6]==bytes.fromhex('ad0020d0034c')
        # Zero follows the absolute JMP over the call; nonzero branches to it.
        assert int.from_bytes(gate[6:8],'little')==(at+7)&65535
    assert offsets(rom,bytes.fromhex('a9ec62'))==[0x36338]
    assert rom[0x58c14:0x58c17]==bytes.fromhex('54e7c2')
    audio=ROOT/'engine/runner/tlk_audio.c'
    assert '{"audio.effects.simba.bounce",0x11,2,123,1,0xc36686}' in audio.read_text()
    paths=[Path(__file__),rom_path,audio]
    report=dict(result='ORIGINAL_PROGRAM17_CALLERS_BOUNDED',
        immediate_cue17_wrapper_returns=[f'{at:06x}' for at in returns],
        current_bounce_leaf_caller='c36686',
        c362ec_direct_calls=[f'{at+0xc00000:06x}' for at in direct],
        all_four_direct_calls_require_nonzero_2000=True,
        other_npc_descriptor_constructor_reference='c58c14 -> c2e754',
        other_npc_caller='c2e99f',other_npc_pride_reachability_proven=False,
        all_indirect_or_computed_callers_proven=False,production_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=ROOT/'build/pride-lizard-launch-work/bounce-native-callers-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n');print(report['result'],report['immediate_cue17_wrapper_returns'],flush=True)


if __name__=='__main__':main()
