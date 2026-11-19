"""Measure recorded restart samples against original MD pixels at native brightness."""
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_sprite_catalog import bitmap
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-caption-lifecycle57';source=base/'report.json';prior=bound(source);assert prior['result']=='PASS'
    out=base/'fade-qualification';out.mkdir();rompath=ROOT/'Lion King, The (World).md';rom=rompath.read_bytes();pieces=[]
    for i in range(11):
        w,h,x,y,flags,transfer,ptr=struct.unpack_from('>6HI',rom,0x1d5dac+24+i*16);pieces.append((x-160,y-72,w,h,ptr))
    bx,by,bw,bh,data=bitmap(rom,pieces,True,with_origin=True)
    palette=[sum(((c>>s&7)*4+((c>>s&7)>>2))<<(n*5) for n,s in enumerate((1,5,9))) for c in struct.unpack_from('>16H',rom,0x1d78aa)]
    points=[(160+bx+i%bw,72+by+i//bw,tuple(((palette[c]>>s&31)<<3)|((palette[c]>>s&31)>>2) for s in (0,5,10))) for i,c in enumerate(data) if c]
    observations=[];paths=[Path(__file__),source,rompath]
    for probe in prior['observations']['restart']['probes']:
        path=base/'restart'/probe['path'];w,h,image=pixels(path);paths.append(path)
        matches=[sum(image[(y*2)*w+x*2]==tuple(c*brightness//15 for c in rgb) for x,y,rgb in points) for brightness in range(1,16)]
        observations.append(dict(field=probe['field'],path=probe['path'],nonblack_pixels=sum(any(pixel) for pixel in image),
                                 best_matching_brightness=1+matches.index(max(matches)),original_pixels_matched=max(matches)))
    black=[r for r in observations if not r['nonblack_pixels']];lit=[r for r in observations if r['nonblack_pixels']]
    checks=dict(original_caption_has1686_opaque_pixels=len(points)==1686,
                eleven_blank_preparation_samples_have_no_caption_leak=len(black)==11 and all(r['original_pixels_matched']==0 for r in black),
                two_lit_samples_observed=len(lit)==2,
                partial_native_fade_sample_matches_all_original_md_pixels=len(lit)==2 and lit[0]['best_matching_brightness']==10 and lit[0]['original_pixels_matched']==1686,
                full_brightness_sample_matches_all_original_md_pixels=len(lit)==2 and lit[1]['best_matching_brightness']==15 and lit[1]['original_pixels_matched']==1686,
                captured_samples_ordered=[r['field'] for r in observations]==sorted(r['field'] for r in observations))
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                sampled_native_brightness_rendering_only=True,original_md_fade_timing_equivalence_verified=False,
                all_intermediate_restart_fields_captured=False,public_preview_unchanged=True,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
