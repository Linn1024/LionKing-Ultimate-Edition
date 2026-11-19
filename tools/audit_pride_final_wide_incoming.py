"""Compare every incoming client pixel with the saved full-width fade source."""
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-final-wide';source=base/'lifecycle/report.json';bound(source)
    out=base/'incoming-pixels';out.mkdir()
    state=base/'lifecycle/incoming/saved.state';data=state.read_bytes()
    fixed=96+struct.unpack_from('<I',data,20)[0]
    field=struct.unpack_from('<I',data,32)[0]
    confirmed=struct.unpack_from('<Q',data,fixed+148)[0]
    age=field-confirmed
    assert 284<=age<302,age
    rise=(((age-281)//3)*31+3)//7
    centre=struct.unpack_from('<'+str(256*224)+'I',data,fixed+192+3*256*224*4)
    sides=struct.unpack_from('<'+str(64*224)+'I',data,len(data)-64*224*4)
    full=[]
    for y in range(224):
        full.extend(sides[y*64:y*64+32]);full.extend(centre[y*256:(y+1)*256]);full.extend(sides[y*64+32:(y+1)*64])
    expected=[]
    for pixel in full:
        rgb=[]
        for shift in (16,8,0):
            c=min((pixel>>shift&255)>>3,rise);rgb.append(c<<3|c>>2)
        expected.append(tuple(rgb))
    width,height,actual=pixels(base/'lifecycle/incoming/window.png')
    assert (width,height)==(640,448)
    different=[(x,y) for y in range(height) for x in range(width) if actual[y*width+x]!=expected[(y//2)*320+x//2]]
    checks=dict(incoming_phase_measured=True,whole_client_matches=not different,
        left_margin_matches=not any(x<64 for x,y in different),
        right_margin_matches=not any(x>=576 for x,y in different))
    paths=[Path(__file__),source,state]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        field=field,confirmed_field=confirmed,age=age,rise=rise,compared_pixels=len(actual),
        differing_pixels=len(different),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],report['differing_pixels'],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
