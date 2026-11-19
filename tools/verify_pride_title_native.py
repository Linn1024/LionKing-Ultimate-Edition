"""Check decoded native caption glyphs against its actual Windows raster."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels
from pride_sprite_catalog import bitmap


def main():
    out=ROOT/'build/pride-title-native-check';out.mkdir()
    source_path=ROOT/'build/pride-title-art-review2/report.json'
    source=json.loads(source_path.read_text())
    rom_path=ROOT/'Lion King, The (USA).sfc';rom=rom_path.read_bytes()
    folder=ROOT/'build/pride-intro-windows/256-1000'
    scene_path=folder/'scene.json';image_path=folder/'window.png'
    scene=json.loads(scene_path.read_text());palette=scene['obj_palette0'];w,h,picture=pixels(image_path)
    tested=0;mismatches=[]
    for row in source['glyph_matches']:
        record=row['native_record'];at=int(record['source'],16)&0x3fffff
        x,y,gw,gh,data=bitmap(rom,[(0,0,16,16,at)],False,with_origin=True)
        for i,c in enumerate(data):
            if not c:continue
            px=16+record['x']+x+i%gw;py=48+record['y']+y+i//gw
            expected=tuple(((palette[c]>>shift&31)<<3)|((palette[c]>>shift&31)>>2) for shift in (0,5,10))
            actual=picture[(py*3+1)*w+px*3+1];tested+=1
            if actual!=expected:mismatches.append([px,py,actual,expected])
    assert tested==1366
    paths=[Path(__file__),source_path,rom_path,scene_path,image_path]
    report=dict(result='PASS' if not mismatches else 'FAIL',opaque_pixels_verified=tested,
                mismatches=mismatches,only_native_caption_decoder_verified=True,
                md_semantic_owner_verified=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],tested,'native caption pixels versus actual client',flush=True)
    assert not mismatches


if __name__=='__main__':main()
