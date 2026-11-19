"""Bind the verified popup candidate; full Pride and preview promotion stay open."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_popup_history import bound


def main():
    base=ROOT/'build/pride-popup-work'
    build_path=base/'commands4.json';build=bound(build_path)
    binary=base/'player/native-engine/tlk_pride_player.exe'
    assert digest(binary)==build['binary_sha256']
    reports=['guards4/report.json','player-check4/report.json','client-audit/report.json',
             'tree/report.json','schema/report.json','completion/report.json']
    checks={};sources={};counts={}
    for name in reports:
        p=base/name;r=bound(p);assert r['result']=='PASS',name
        assert all(r['checks'].values()),name
        counts[name]=len(r['checks'])
        checks.update({name+'/'+k:v for k,v in r['checks'].items()})
        sources[p.relative_to(ROOT).as_posix()]=digest(p)
    report=dict(result='PARTIAL',scope='Verified popup artwork/palette/position candidate; full Pride remains incomplete',
                verified_component_checks=len(checks),component_counts=counts,
                binary=binary.relative_to(ROOT).as_posix(),binary_sha256=digest(binary),
                public_preview_promoted=False,full_first_level_fidelity_complete=False,
                pending=['Native route regression verification before preview promotion'],
                source_sha256={**sources,build_path.relative_to(ROOT).as_posix():digest(build_path),
                               Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__))})
    dest=base/'candidate-report.json';assert not dest.exists()
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'popup component checks; preview promotion pending',flush=True)


if __name__=='__main__':main()
