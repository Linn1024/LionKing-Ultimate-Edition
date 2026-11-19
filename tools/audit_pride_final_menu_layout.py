"""Establish original menu right-edge anchors and measure the preceding crop."""
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-final-menu-layout-evidence';out.mkdir();checks={}
    mdfile=ROOT/'Lion King, The (World).md';snesfile=ROOT/'Lion King, The (USA).sfc'
    md=mdfile.read_bytes();snes=snesfile.read_bytes()
    checks['verified_md']=digest(mdfile)=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    checks['verified_snes']=digest(snesfile)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    checks['snes_icon_push_x176']=snes[0x8c6a:0x8c6d]==bytes.fromhex('f4 b0 00')
    checks['snes_digit_column24']=snes[0x8e89:0x8e8c]==bytes.fromhex('f4 18 00')
    checks['snes_text_column_times8']=snes[0x5387e:0x53883]==bytes.fromhex('a3 08 0a 0a 0a')
    mdicon=struct.unpack_from('>H',md,0x1d6a00)[0];mddigit=struct.unpack_from('>H',md,0x1d69e2)[0]
    checks['original_right_edge_icon_distance80']=320-mdicon==256-176==80
    checks['original_right_edge_digit_distance64']=320-mddigit==256-24*8==64
    native_report=ROOT/'build/pride-final-menu-player9/continue/report.json';bound(native_report)
    scene=native_report.parent/'256-native160/scene.json';pieces=json.loads(scene.read_text())['pieces']
    icons=[p for p in pieces if p.get('actor_descriptor')==0xc586cc]
    checks['actual_native_icon_anchor']=bool(icons) and all(p['actor_xy']==[176,195] for p in icons)
    manifest=ROOT/'build/pride-final-menu-scene/installed/install.json';info=json.loads(manifest.read_text());package=manifest.parent/info['menu_assets']['file']
    raw=package.read_bytes();p=240;images={}
    for i in range(struct.unpack_from('<I',raw,20)[0]):
        frame,x,y,w,h=struct.unpack_from('<IiiII',raw,p);p+=20
        images[frame]=(x,y,w,h,raw[p:p+w*h]);p+=w*h
    slots=struct.unpack_from('<13I',raw,p);coords=struct.unpack_from('<8i',raw,p+52)
    checks['installed_anchors_match_rom']=(coords[4],coords[6])==(mdicon,mddigit)
    rows=[]
    for digit,frame in enumerate(slots[3:]):
        x,y,w,h,pixels=images[frame];xs=[i%w+x+coords[6] for i,v in enumerate(pixels) if v]
        crop=[min(xs)-32,max(xs)-32];anchored=[min(xs)-64,max(xs)-64]
        checks[f'digit{digit}_old_crop_was_not_clipped']=0<=crop[0]<=crop[1]<256
        checks[f'digit{digit}_right_edge_layout_fits']=0<=anchored[0]<=anchored[1]<256
        rows.append(dict(digit=digit,old_crop_x=crop,right_edge_x=anchored))
    paths=[Path(__file__),mdfile,snesfile,native_report,scene,manifest,package]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,digits=rows,
        correction='Previous visual claim of digit clipping was wrong; old crop fits but changes the right-edge distance by32 pixels',
        policy='Preserve original MD vertical positions/art; anchor icon/digit to the right edge using distances independently shared by both original widths',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
