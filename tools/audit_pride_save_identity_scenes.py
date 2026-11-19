"""Compare every scene's render/layer/font/ground artifacts across editor builds."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-save-identity2';checks={};paths=[Path(__file__)];compared=0;rgb_files=0
    selected={'render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','scenery-evidence.json','ground-entry.bin','ground-entry.csv','ground-return.bin','ground-return.csv'}
    def files(folder):return {p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file() and (p.name in selected or p.name.startswith('scenery-evidence.json.bg'))}
    def compare(label,a,b,require_two=False):
        nonlocal compared,rgb_files
        left,right=files(a),files(b);checks[label+'/all_scene_paths']=left.keys()==right.keys()
        if require_two:checks[label+'/two_distinct_scenes']=len([p for p in left.values() if p.suffix=='.rgb'])==2
        checks[label+'/all_scene_bytes']=all(digest(left[k])==digest(right[k]) for k in left if k in right)
        for k in left.keys()&right.keys():compared+=left[k].stat().st_size;rgb_files+=left[k].suffix=='.rgb'
    for profile in ('native','md'):
        path=base/'verified'/profile/'report.json';r=bound(path);assert r['result']=='PASS';paths.append(path);root=path.parent
        compare(profile+'/cold',root/'author-a',root/'author-b',True)
        for direction in ('a-to-b','b-to-a'):
            for kind in ('ordinary','owned','boot'):
                folder=root/direction/kind;compare(profile+'/'+direction+'/'+kind,folder/'control',folder/'cross')
    prior=base/'preceding-cold/report.json';r=bound(prior);assert r['result']=='PASS';paths.append(prior)
    for profile in ('native','md'):compare(profile+'/preceding',base/'preceding-cold'/profile,base/'verified'/profile/'author-a',True)
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,compared_scene_artifact_bytes=compared,compared_rgb_artifacts=rgb_files,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},public_player_enabled=False)
    (base/'scene-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result['result'],compared,'scene bytes;',rgb_files,'RGB artifacts',[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
