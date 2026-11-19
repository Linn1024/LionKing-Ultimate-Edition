"""Compare original ledge stream tokens and their parser-call clock semantics.

Physical display fields, action interruptions and movement are not normalized
or claimed equal by this stream-only audit.
"""
import json
from pathlib import Path

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_ledge_history import bound


def main():
    native_path=ROOT/'build/pride-ledge-native-stream/report.json';native=bound(native_path)
    catalog_path=ROOT/'build/pride-sprites/catalog.json';catalog=json.loads(catalog_path.read_text())
    pairs={int(r['snes'],16)&0x3fffff:{int(p,16) for p in r['md']}
           for group in ('exact_matches','pixel_art_variants') for r in catalog[group]}
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    # Both original parsers decrement the byte timer before a negative result
    # fetches a token. The native shared entry and MD stream-set command clear it.
    assert snes[0xad32:0xad3e]==bytes.fromhex('a01ab1683a916830034c72ad')
    assert md[0x2d42:0x2d48]==bytes.fromhex('5328001a6aba')
    assert md[0x2d36:0x2d40]==bytes.fromhex('201e214000124228001a')
    # For this0x80 control byte none of the preceding explicit controls match;
    # original2DBE loads the pointer and branches back into the fetch loop.
    assert md[0x2dbe:0x2dc2]==bytes.fromhex('2a55608a')
    start=0x7ef2e;tokens=[]
    for index,old in enumerate(native['tokens']):
        at=start+index*4;duration=md[at];pose=int.from_bytes(md[at+1:at+4],'big')
        assert duration==old['duration']<128
        assert pose in pairs[int(old['pose'],16)&0x3fffff],(index,old,hex(pose))
        tokens.append(dict(duration=duration,native_pose=old['pose'],md_pose=f'{pose:06x}',parser_calls_per_pose=duration+1))
    marker=start+len(tokens)*4;encoded=int.from_bytes(md[marker:marker+4],'big')
    assert md[marker]==0x80
    target=encoded&0xffffff;assert start<=target<marker and (target-start)%4==0
    loop=(target-start)//4;assert loop==native['loop_to_token']==21
    out=ROOT/'build/pride-ledge-stream-pair';out.mkdir()
    paths=[Path(__file__),native_path,catalog_path]
    report=dict(result='ORIGINAL_LEDGE_STREAM_PROTOCOLS_CORRESPOND',tokens=tokens,md_control=f'{encoded:08x}',
        md_24bit_bus_target=f'{target:06x}',loop_to_token=loop,
        native_ff_and_md_80_loop_encodings_differ=True,matching_visible_tokens=26,
        parser_calls_per_pose_equal=True,physical_frame_or_interruptions_equivalence_proven=False,
        production_gameplay_timing_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'26 reviewed pose/duration pairs; same loop21, different control encoding',flush=True)


if __name__=='__main__':main()
