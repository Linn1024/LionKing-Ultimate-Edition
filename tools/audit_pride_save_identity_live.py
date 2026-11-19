"""Audit actual cross-build F5 with the documented practice-panel toast position."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import pixels


def practice_toast(reference):
    w,h,data=pixels(reference);assert h==448 and w in (512,640)
    message='Loaded slot 1';font=(ROOT/'engine/runner/tlk_font8x8.h').read_text()
    glyphs=[[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',row)] for row in re.findall(r'\{([^{}]+)\}',font)]
    extra=(w//2-256)//2
    for y in range(24,40):
        for x in range(4,4+len(message)*8+8):
            white=False
            if 28<=y<36 and 8<=x<8+len(message)*8:
                white=bool(glyphs[ord(message[(x-8)//8])-32][y-28]&(1<<((x-8)%8)))
            for dy in (0,1):
                for dx in (0,1):
                    at=(y*2+dy)*w+(extra+x)*2+dx
                    data[at]=(255,255,255) if white else tuple(v*25//255 for v in data[at])
    return w,h,data


def main():
    base=ROOT/'build/pride-save-identity2';paths=[Path(__file__),ROOT/'engine/runner/tlk_font8x8.h',ROOT/'engine/runner/sdl_main.c'];checks={};fields=0;pixel_count=0
    for profile in ('native','md'):
        path=base/'live'/profile/'report.json';raw=bound(path);assert raw['result']=='INCOMPLETE'
        assert [k for k,v in raw['checks'].items() if not v]==['whole_client_oracle'];paths.append(path)
        for key,value in raw['checks'].items():
            if key!='whole_client_oracle':checks[profile+'/'+key]=value
        checks[profile+'/whole_practice_client_oracle']=pixels(path.parent/'live/window.png')==practice_toast(path.parent/'control/window.png')
        fields+=raw['native_fields_compared'];pixel_count+=(640 if profile=='md' else 512)*448
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,native_fields_compared=fields,independent_complete_client_pixels=pixel_count,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},public_player_enabled=False)
    (base/'live-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result['result'],fields,'guest fields;',pixel_count,'client pixels',[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
