"""Bind the selectable caption and HUD-priority component evidence."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_title_history import bound


def main():
    base=ROOT/'build/pride-title-work';bp=base/'final-build3.json';build=bound(bp)
    binary=base/'player/native-engine/tlk_pride_player.exe';assert digest(binary)==build['binary_sha256']
    reports=['assets2/report.json','original-sat/report.json','player-check3/report.json','entrance3/report.json',
             'tree/report.json','schema/report.json','completion/report.json','hud-priority/report.json','retirement/report.json']
    count=0;counts={};sources={}
    for name in reports:
        p=base/name;r=bound(p);assert r['result']=='PASS' and all(r['checks'].values()),name
        counts[name]=len(r['checks']);count+=len(r['checks']);sources[p.relative_to(ROOT).as_posix()]=digest(p)
    resource_log=base/'resources-test/1.log';assert 'resources_test: PASS (0 failed)' in resource_log.read_text()
    count+=1
    paths=[Path(__file__),bp,resource_log,base/'resources-test/0.log',ROOT/'engine/tests/resources_test.c']
    result=dict(result='PARTIAL',verified_component_checks=count,component_counts=counts,
                normal_resources_test_passed=True,binary=binary.relative_to(ROOT).as_posix(),binary_sha256=digest(binary),
                public_preview_promoted=False,full_first_level_fidelity_complete=False,
                native_display_brightness_preserved=True,owned_health_death_caption_context_not_verified=True,
                pending=['native route regression before promotion'],
                source_sha256={**sources,**{p.relative_to(ROOT).as_posix():digest(p) for p in paths}})
    dest=base/'candidate-report.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL',count,'caption/HUD component checks; preview promotion pending',flush=True)


if __name__=='__main__':main()
