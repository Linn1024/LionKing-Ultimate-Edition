"""Prove resolution of the retained80 full-route gameplay regression."""
import json
from pathlib import Path
import re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    old=ROOT/'build/pride-menu-audio80/route/report.json';a=bound(old)
    current=ROOT/'build/pride-menu-output83/route/report.json';b=bound(current)
    isolation=ROOT/'build/pride-menu-output84-isolation/report.json';c=bound(isolation)
    checks=dict(retained80_failed=a['result']=='FAIL',current_route_passes=b['result']=='PASS' and all(b['checks'].values()),
                all_four_independent_effects_verified=c['result']=='PASS' and all(c['checks'].values()))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    paths=[Path(__file__),old,current,isolation];observations={}
    for path in (old,current):
        native=re.findall(pattern,(path.parent/'native/run.log').read_text())
        for mode in ('aot','lle'):
            selected=re.findall(pattern,(path.parent/('menus-'+mode)/'run.log').read_text())
            mismatches=[int(x[0]) for x,y in zip(native,selected) if x[1]!=y[1]]
            key=path.parent.parent.name+'-'+mode
            observations[key]=dict(picture_mismatches=len(mismatches),first_picture_mismatch=min(mismatches) if mismatches else None,
                                   full_guest_fields_equal=native==selected)
            if path==current:checks[mode+'_all6000_picture_and_full_wram_fields_equal']=len(selected)==len(native)==6000 and selected==native
            else:checks[mode+'_retained80_first_picture_mismatch5636']=min(mismatches)==5636
            paths += [path.parent/'native/run.log',path.parent/('menus-'+mode)/'run.log']
    out=current.parent.parent/'regression';out.mkdir()
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                full_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
