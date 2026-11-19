"""Measure each original MD video field around final-life fade and Continue."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels
import capture_pride_final_presentation as capture


def main():
    out=ROOT/'build/pride-final-fade';out.mkdir()
    capture.OFFSETS=tuple(range(121))
    data,paths=capture.original(out)
    observed=[];matches=[]
    for offset in range(121):
        path=out/f'{offset:03d}.png';w,h,picture=pixels(path)
        observed.append(dict(offset=offset,nonblack=sum(p!=(0,0,0) for p in picture),peak=max(max(p) for p in picture)))
        preceding=ROOT/'build/pride-final-presentation/md'/path.name
        if preceding.exists():
            assert digest(path)==digest(preceding),offset
            matches.append(offset)
    first_black=next(r['offset'] for r in observed if not r['nonblack'])
    first_return=next(r['offset'] for r in observed if r['offset']>first_black and r['nonblack'])
    paths += [Path(__file__),ROOT/'tools/capture_pride_final_presentation.py',ROOT/'build/pride-final-presentation/md/report.json']
    report=dict(result='MEASURED',first_black_video_offset=first_black,first_continue_pixels_video_offset=first_return,
                observations=observed,preceding_picture_offsets_preserved=matches,original_run=data,
                final_life_adapter_implemented=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original final-life: first black',first_black,'first Continue pixels',first_return,flush=True)


if __name__=='__main__':main()
