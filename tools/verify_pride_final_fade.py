"""Verify final-life fade against every captured original display pixel."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-final-fade';out=base/'verified';out.mkdir()
    source=bound(base/'report.json');assert source['result']=='MEASURED'
    first=pixels(base/'000.png');last=pixels(base/'120.png')
    levels=[[0,32,65,98,139,172,205,238],[0,32,68,101,137,170,206,238],[0,32,65,98,139,172,205,238]]
    def indexed(image):return [tuple(levels[c].index(p[c]) for c in range(3)) for p in image]
    frozen=indexed(first[2]);target=indexed(last[2]);checks={};tested=0
    for n in range(121):
        w,h,actual=pixels(base/f'{n:03d}.png');assert (w,h)==first[:2]==(320,224)
        if n<25:
            loss=(n+2)//3
            expected=[tuple(levels[c][max(0,p[c]-loss)] for c in range(3)) for p in frozen]
        elif n<97:expected=[(0,0,0)]*len(frozen)
        else:
            rise=(n-97)//3
            expected=[tuple(levels[c][min(p[c],rise)] for c in range(3)) for p in target]
        checks[str(n)+'/original_pixels']=expected==actual;tested+=len(actual)
    paths=[Path(__file__),base/'report.json',ROOT/'engine/runner/pride/wide/pride_repeat_render_wide.c']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,pixels_compared=tested,
        original_first_black=19,original_first_continue_pixels=100,
        frozen_final_hit_fade_loss='(age+2)/3',continue_fade_rise='(age-97)/3 from age97',
        palette_levels_are_reference_rgb565_conversion=True,final_life_adapter_implemented=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],tested,'original final-scene pixels',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
