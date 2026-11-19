"""Verify the cub animation shared by all original native ledge-tag branches."""
import json
from pathlib import Path

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_ledge_history import bound


def main():
    tag_path=ROOT/'build/pride-ledge-tags/report.json';tags=bound(tag_path)
    assert tags['result']=='ORIGINAL_LEDGE_TAG_BRANCHES_MATCH'
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    selector=bytes.fromhex('f4c000f4f9e6f4c000f459e622d296c1')
    for at in (0x351ee,0x353c0):assert rom[at:at+len(selector)]==selector
    # Original C196D2 selects the first stack pointer for cub age0.
    assert rom[0x196d2:0x196d7]==bytes.fromhex('ad0020f00b')
    assert rom[0x196e2:0x196ed]==bytes.fromhex('a3048d8ea6a3068d90a66b')
    # Shared C0E659 installs the native F116 stream, bank C0, timer0.
    stub=bytes.fromhex('a916f1a0129168e220a9c0a0149168a900a01a9168')
    assert rom[0xe659:0xe659+len(stub)]==stub
    start=0xf116;tokens=[];loop=None
    for index in range(128):
        at=start+index*4;duration=rom[at];value=int.from_bytes(rom[at+1:at+4],'little')
        if duration==255:
            assert start<=(value&0x3fffff)<at and ((value&0x3fffff)-start)%4==0
            loop=((value&0x3fffff)-start)//4;break
        assert duration<128,'Native ledge stream contains a control command requiring separate review'
        tokens.append(dict(duration=duration,pose=f'{value:06x}'))
    assert len(tokens)==26 and loop==21
    out=ROOT/'build/pride-ledge-native-stream';out.mkdir()
    paths=[Path(__file__),tag_path]
    report=dict(result='NATIVE_SHARED_LEDGE_STREAM_HAS_NO_SOUND_COMMANDS',cub_handler='C0E659',stream='C0F116',
        tokens=tokens,loop_to_token=loop,matching_tag_count_per_direction=17,
        shared_by_both_helpers=True,other_actor_interruptions_or_md_timing_proven=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'26 pose-only tokens, loop21; all17 ledge tags share this cub entry',flush=True)


if __name__=='__main__':main()
