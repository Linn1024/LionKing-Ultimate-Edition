"""Verify the separate original single-life Game Over transition, pixel by pixel."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-hard-final-reference';out=base/'verified';out.mkdir()
    source=bound(base/'report.json');assert source['result']=='CAPTURED'
    first=pixels(base/'final-000.png');last=pixels(base/'final-120.png')
    levels=[[0,32,65,98,139,172,205,238],[0,32,68,101,137,170,206,238],[0,32,65,98,139,172,205,238]]
    indexed=lambda image:[tuple(levels[c].index(p[c]) for c in range(3)) for p in image]
    frozen=indexed(first[2]);target=indexed(last[2]);checks={};nonblack=[]
    checks['one_ordinary_life_exhausted']=source['life_losses']==[dict(field=source['fatal_field'],before=1,after=0,health=0)]
    for n in range(121):
        w,h,actual=pixels(base/f'final-{n:03d}.png');assert (w,h)==first[:2]==(320,224)
        if n<25:
            loss=(n+2)//3
            expected=[tuple(levels[c][max(0,p[c]-loss)] for c in range(3)) for p in frozen]
        elif n<97:expected=[(0,0,0)]*len(frozen)
        else:
            rise=(n-97)//3
            expected=[tuple(levels[c][min(p[c],rise)] for c in range(3)) for p in target]
        checks[str(n)+'/original_pixels']=expected==actual
        nonblack.append(sum(p!=(0,0,0) for p in actual))
    first_black=next(n for n,count in enumerate(nonblack) if count==0)
    first_return=next(n for n,count in enumerate(nonblack) if n>first_black and count)
    checks['same_black_boundary_as_continue_context']=first_black==19
    checks['same_visible_boundary_as_continue_context']=first_return==100
    paths=[Path(__file__),base/'report.json',ROOT/'build/pride-final-fade/verified/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,pixels_compared=121*320*224,
        original_single_life_gameover_first_black=first_black,original_first_gameover_pixels=first_return,
        difficulty_name_not_inferred_from_pre_input_menu_picture=True,final_life_adapter_implemented=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'single-life Game Over: black',first_black,'visible',first_return,flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
