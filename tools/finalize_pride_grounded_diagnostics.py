"""Close capture manifests after the parent-owned stdout log finishes.

The child hashes its directory before printing its terminal status. Preserve
that original manifest, validate every game artifact unchanged, and bind the
now-closed diagnostic stream without relabeling any captured game evidence.
"""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-grounded';count=0
    for path in sorted(base.rglob('report.json')):
        r=json.loads(path.read_text());folder=path.parent
        if 'exit_code' not in r or not (folder/'driver.log').exists():continue
        if 'closed_stdout_manifest' in r:
            for n,sha in r['artifacts_sha256'].items():assert digest(folder/n)==sha,(path,n)
            assert r['source_sha256']['tools/finalize_pride_grounded_diagnostics.py']==digest(Path(__file__))
            count+=1;continue
        assert r['exit_code']==0
        expected=f"{r['width']} {r['graphics']} {r['execution']} {r['host']} exit 0\n"
        assert (folder/'driver.log').read_text()==expected,(path,'terminal stdout')
        assert r['artifacts_sha256']['driver.log']=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        for n,sha in r['artifacts_sha256'].items():
            if n!='driver.log':assert digest(folder/n)==sha,(path,n)
        for n,sha in r['source_sha256'].items():assert digest(ROOT/n)==sha,n
        archive=folder/'child-report-before-stdout-close.json';assert not archive.exists()
        archive.write_bytes(path.read_bytes())
        r['closed_stdout_manifest']=dict(original_child_manifest_sha256=digest(archive),
            original_stdout_bytes=0,closed_stdout_sha256=digest(folder/'driver.log'),game_artifacts_changed=False)
        r['artifacts_sha256']['driver.log']=digest(folder/'driver.log')
        r['artifacts_sha256'][archive.name]=digest(archive)
        r['source_sha256']['tools/finalize_pride_grounded_diagnostics.py']=digest(Path(__file__))
        path.write_text(json.dumps(r,indent=2)+'\n');count+=1
    assert count==46,count
    print('Closed stdout manifests for46 captures; original child manifests and all game evidence preserved',flush=True)


if __name__=='__main__':main()
