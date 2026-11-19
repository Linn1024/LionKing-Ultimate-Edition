"""Bind observed last-life presentation differences without claiming an adapter."""
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-final-presentation';out=base/'audit';out.mkdir()
    original=bound(base/'md/report.json');preview=bound(base/'preview/report.json')
    checks=dict(original_final_life_observed=original['captures'][0]['health']==0 and original['captures'][0]['lives']==0,
                preview_final_life_observed=preview['captures'][1]['gameplay']['health']==0 and preview['captures'][1]['gameplay']['lives']==0)
    observations={}
    for source,report in [('md',original),('preview',preview)]:
        rows=[]
        for row in report['captures']:
            offset=row['offset']
            if offset<0:continue
            path=base/source/(f'{offset:03d}.png' if source=='md' else f'{offset}/window.png')
            width,height,data=pixels(path)
            rows.append(dict(offset=offset,nonblack_pixels=sum(p!=(0,0,0) for p in data),
                             peak=max(max(p) for p in data),width=width,height=height))
        observations[source]=rows
    md={r['offset']:r for r in observations['md']};native={r['offset']:r for r in observations['preview']}
    checks['original_scenery_still_visible_at_8']=md[8]['nonblack_pixels']>1000
    checks['original_black_by_24']=md[24]['nonblack_pixels']==0
    checks['original_black_at_88_and_96']=md[88]['nonblack_pixels']==md[96]['nonblack_pixels']==0
    checks['original_continue_visible_by_104']=md[104]['nonblack_pixels']>1000
    checks['preview_native_display_still_visible_at_88']=native[88]['nonblack_pixels']>100
    positions=[]
    for offset in (0,4,8,12,16,20,24):
        data=(base/'md'/f'{offset:03d}-wram.bin').read_bytes();w=lambda a:struct.unpack_from('<H',data,a)[0]
        actor=w(w(0xcd36)+36)
        positions.append([actor,w(actor+8),w(actor+10)])
    checks['original_fatal_actor_stationary_through_fade']=positions==[[0x934e,1525,336]]*len(positions)
    paths=[Path(__file__),base/'md/report.json',base/'preview/report.json']
    report=dict(result='OBSERVED_DIFFERENCE' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
        original_actor_positions=positions,exact_first_visible_field_not_measured=True,final_life_adapter_implemented=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'final display observations',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
