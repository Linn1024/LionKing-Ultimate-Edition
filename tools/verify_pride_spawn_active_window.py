"""Compare real ready+2 clients with identical gameplay and differing scene ownership."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-spawn-revival';captures=[];sources={}
    for name,presenter in (('active-window-owned','owned'),('active-window-native','native')):
        folder=base/name;path=folder/'report.json';r=json.loads(path.read_text())
        assert r['exit_code']==0 and r['frames']==2331 and r['presenter']==presenter and r['start_source']=='md'
        assert not r['loaded_states'] and not r['guest_fixture_edits']
        for file,sha in r['artifacts_sha256'].items():assert digest(folder/file)==sha,(name,file)
        for file,sha in r['source_sha256'].items():assert digest(ROOT/file)==sha,file
        sources[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);captures.append((folder,r))
    (a,ar),(b,br)=captures
    assert len(ar['guest'])==2 and ar['guest']==br['guest'] and ar['binary_sha256']==br['binary_sha256']==digest(base/'spawn-revival-sdl.exe')
    for name in ('owner-fields.csv','post-ready.csv','spawn-policy.csv'):assert digest(a/name)==digest(b/name),name
    w,h,owned=pixels(a/'window.png');rw,rh,native=pixels(b/'window.png');assert (w,h)==(rw,rh)==(640,448)
    bad=[i for i,(x,y) in enumerate(zip(owned,native)) if x!=y]
    box=[min(i%w for i in bad),min(i//w for i in bad),max(i%w for i in bad),max(i//w for i in bad)] if bad else None
    for p in (Path(__file__),ROOT/'tools/verify_windows.py'):sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    report=dict(result='ACTIVE_PRESENTER_FAILURE_REPRODUCED' if bad else 'CLIENTS_MATCH',guest_equal=True,
        client_difference_pixels=len(bad),client_difference_bbox=box,width=w,height=h,source_sha256=sources,
        full_first_level_fidelity_complete=False)
    (base/'active-window-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'difference',len(bad),'bbox',box,flush=True)
    if bad:raise SystemExit(1)


if __name__=='__main__':main()
