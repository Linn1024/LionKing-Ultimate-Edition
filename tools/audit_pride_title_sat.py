"""Tie the original caption task to every displayed MD piece/texture pixel."""
import csv
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    source=ROOT/'build/pride-title-original2';out=ROOT/'build/pride-title-work/original-sat';out.mkdir()
    parent=source/'report.json';capture=json.loads(parent.read_text())
    assert capture['result']=='ORIGINAL_CAPTION_TASK_VERIFIED'
    for name,sha in capture['artifacts_sha256'].items():assert digest(source/name)==sha
    calls=list(csv.DictReader((source/'calls.csv').open()))
    md_path=ROOT/'Lion King, The (World).md';md=md_path.read_bytes()
    pieces=[struct.unpack_from('>6HI',md,0x1d5dac+24+i*16) for i in range(11)]
    checks={};observations=[]
    for field in (1360,1400,1440):
        folder=source/str(field);vram=(folder/'vram.bin').read_bytes();reg=(folder/'reg.bin').read_bytes()
        word=lambda a:struct.unpack_from('<H',vram,a)[0]
        base=(reg[5]&0x7e)<<9;sprites=[];seen=set();slot=0
        while slot not in seen:
            seen.add(slot);at=base+slot*8;size=word(at+2)
            sprites.append(dict(x=(word(at+6)&511)-128,y=(word(at)&511)-128,
                w=(((size>>10)&3)+1)*8,h=(((size>>8)&3)+1)*8,attr=word(at+4)))
            slot=size&127
            if not slot:break
        matches=[];pixels=0
        for start in range(len(sprites)-len(pieces)+1):
            good=True;checked=0
            for sprite,(w,h,x,y,flags,transfer,texture) in zip(sprites[start:],pieces):
                if (sprite['x'],sprite['y'],sprite['w'],sprite['h'])!=(x,y,w,h) or sprite['attr']&0x7800:good=False;break
                for dy in range(h):
                    for dx in range(w):
                        relative=(dx//8*(h//8)+dy//8)*32+(dy&7)*4+(dx&7)//2
                        v=(vram[(((sprite['attr']&2047)*32+relative)&65535)^1]>>(0 if dx&1 else 4))&15
                        expected=md[texture+relative]>>(0 if dx&1 else 4)&15
                        if v!=expected:good=False;break
                        checked+=1
                    if not good:break
                if not good:break
            if good:matches.append(start);pixels=checked
        active=[r for r in calls if int(r['field'])==field and r['level']=='1']
        checks[f'{field}/actual_task_and_sat']=len(matches)==1 and bool(active) if field<1440 else not matches and not active
        observations.append(dict(field=field,matching_sat_blocks=matches,verified_indexed_pixels=pixels,executed_task_calls=len(active)))
    paths=[Path(__file__),parent,md_path]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],observations,flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
