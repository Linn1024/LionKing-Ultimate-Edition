"""Independently compare owned checkpoint base pixels during private revival.

The generic scene proof separately reconstructs complete faded final frames.
This check isolates the checkpoint's source art/palette before the hero overlay.
"""
import argparse
import array
import hashlib
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from pride_sprite_catalog import bitmap,md_frame


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--width',type=int,choices=(256,320),default=320)
    parser.add_argument('--checkpoint',choices=('palette','both'),default='both')
    args=parser.parse_args()
    folder=ROOT/f'build/pride-scene-render-prepared-headless-{args.width}-5400-checkpoint-{args.checkpoint}'
    parent=folder/'report.json';report=json.loads(parent.read_text())
    assert report['result']=='OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN'
    assert report['prepared_objects'] and report['checkpoint_sources']==args.checkpoint
    assert report['probe_sha256']==digest(ROOT/'engine/build-win/tlk_scene_prepared_probe.exe')
    for path,sha in report['source_sha256'].items():assert digest(ROOT/path)==sha,path
    case=folder/'native-owned';run=report['runs']['native-owned']
    for path,sha in run['artifacts_sha256'].items():assert digest(case/path)==sha,path
    assert run['md_base_palette_observed'] and run['black_reload_and_restore_verified']
    rom_path=ROOT/'Lion King, The (World).md';rom=rom_path.read_bytes()
    left,top,w,h,indexed=bitmap(rom,md_frame(rom,0x973b6),True,with_origin=True)
    assert (left,top,w,h)==(-58,-72,33,31)
    palette=[]
    for raw in struct.unpack_from('>16H',rom,0x1d78aa):
        rgb=[((raw>>s)&7)*4+(((raw>>s)&7)>>2) for s in (1,5,9)]
        palette.append(sum((c*8+c//4)<<shift for c,shift in zip(rgb,(16,8,0))))
    compared=0;observations=[];count=args.width*224
    with (case/'render-owned.rgb').open('rb') as data:
        assert data.read(8)==b'PRDRGB01' and struct.unpack('<II',data.read(8))==(args.width,224)
        while header:=data.read(24):
            age,pose,x,y,flip,md=struct.unpack('<IIiiII',header)
            data.read(32)
            full=array.array('I');full.frombytes(data.read(count*4))
            tags=array.array('I');tags.frombytes(data.read(count*4))
            actual=data.read(count*4);assert len(actual)==count*4
            if age<270:continue
            marked={n for n,tag in enumerate(tags) if tag&0xffffff==0xff0000}
            assert len(marked)==657,(age,len(marked))
            x0=min(n%args.width for n in marked);y0=min(n//args.width for n in marked)
            expected={}
            for py in range(h):
                for px in range(w):
                    index=indexed[py*w+px]
                    if index:expected[(y0+py)*args.width+x0+px]=palette[index]
            assert marked==set(expected),(age,'source mask')
            assert all(full[n]==color for n,color in expected.items()),(age,'MD source palette')
            observations.append(dict(age=age,origin=[x0-left,y0-top],pixels=len(marked)))
            compared+=len(marked)
    assert observations and observations[0]['age']==270 and observations[-1]['age']==run['release_age']
    output=ROOT/'build/pride-checkpoint-player'/f'private-checkpoint-{args.width}-{args.checkpoint}-pixels.json'
    result=dict(result='PASS',scope=__doc__,source_head_pixels=compared,fields=observations,
        source_palette_md=True,whole_final_frames_reconstruction_report=str(parent.relative_to(ROOT)),
        actual_windows_captured=False,production_death_behavior_enabled=False,
        full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in
                       (Path(__file__),parent,case/'capture.json',case/'render-owned.rgb',rom_path,
                        ROOT/'tools/pride_sprite_catalog.py')})
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(str(compared)+' original MD source-head pixels exact during owned revival; generic final-frame proof also bound',flush=True)


if __name__=='__main__':main()
