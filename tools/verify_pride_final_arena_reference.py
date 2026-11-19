"""Check every original arena final-life picture against its measured phase model."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-final-arena-original';source=base/'report.json';bound(source)
    out=base/'verified2';out.mkdir()
    first=pixels(base/'final-000.png');last=pixels(base/'final-120.png')
    levels=[[0,32,65,98,139,172,205,238],[0,32,68,101,137,170,206,238],[0,32,65,98,139,172,205,238]]
    indexed=lambda image:[tuple(levels[c].index(p[c]) for c in range(3)) for p in image]
    origin=indexed(first[2]);latched=indexed(pixels(base/'final-001.png')[2]);target=indexed(last[2]);checks={};counts=[]
    for age in range(121):
        w,h,actual=pixels(base/f'final-{age:03d}.png');assert (w,h)==(320,224)
        if age==0:expected=first[2]
        elif age<25:
            loss=(age+2)//3-1;expected=[tuple(levels[c][max(0,p[c]-loss)] for c in range(3)) for p in latched]
        elif age<97:expected=[(0,0,0)]*len(origin)
        else:
            rise=(age-97)//3;expected=[tuple(levels[c][min(p[c],rise)] for c in range(3)) for p in target]
        checks[str(age)+'_whole_picture']=expected==actual;counts.append(sum(any(p) for p in actual))
    black=next(i for i,n in enumerate(counts) if not n);visible=next(i for i,n in enumerate(counts) if i>black and n)
    checks['black19']=black==19;checks['destination100']=visible==100
    latch=base/'latch/report.json';metadata=bound(latch)['rows'];a,b,c=metadata[1:]
    checks['camera_stable_after_fatal']=a['camera']==b['camera']==c['camera']
    checks['foreground_pending_once']=a['horizontal_scroll'][0]!=b['horizontal_scroll'][0]==c['horizontal_scroll'][0]
    checks['background_and_vertical_stable']=a['horizontal_scroll'][1]==b['horizontal_scroll'][1]==c['horizontal_scroll'][1] and a['vertical_scroll']==b['vertical_scroll']==c['vertical_scroll']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,pixels_compared=121*320*224,
        first_black=black,first_destination=visible,
        age1_picture_is_already_faded=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),source,latch]})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],len(checks),'original arena checks',flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
