"""Retain cold-verified control prefixes without claiming level completion."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player3';paths=[Path(__file__)];plans={}
    preceding=ROOT/'build/pride-width-latest.json';p=bound(preceding)
    assert p['result']=='PARTIAL' and p['new_checks']==85;paths.append(preceding)
    bp=base/'width-observer/build-report.json';build=bound(bp);paths.append(bp)
    for name in ('width-plan5','width-plan6','width-plan7','width-plan8'):
        folder=base/name;rp=folder/'report.json';r=bound(rp)
        assert r['result']=='PARTIAL' and not r['next_level_reached']
        assert r['headless_sha256']==build['binary_sha256'] and r['uninterrupted_full_wram_matches_planning']
        tape=folder/'best.polled.tape';assert digest(tape)==r['selected_tape_sha256']
        search_path=folder/'search.json';search=json.loads(search_path.read_text())
        chosen=ROOT/search['generations'][-1][0]['folder'];ram=f"wram-{r['final_frame']}.bin"
        assert (folder/'uninterrupted'/ram).read_bytes()==(chosen/ram).read_bytes()
        paths.extend([rp,tape,search_path,folder/'uninterrupted'/ram,chosen/ram])
        plans[name]=dict(final_frame=r['final_frame'],final=r['final'],waypoint_reached=r['waypoint_reached'])
    assert plans['width-plan6']['waypoint_reached'] and plans['width-plan6']['final_frame']==1720
    assert plans['width-plan8']['waypoint_reached'] and plans['width-plan8']['final_frame']==2040
    for relative in ('width-right-branch/report.json','width-right-branch-cold/report.json','width-upper-phases/report.json'):
        rp=base/relative;r=bound(rp);paths.append(rp)
        assert r['result'] in ('PASS','CAPTURED'),relative
    report=dict(result='PARTIAL',prefixes=plans,latest_verified_frame=2040,
        latest_verified_player=[1032,229],normal_rng_on_256_completion_verified=False,
        compiled_interpreted_new_route_verified=False,full_first_level_fidelity_complete=False,
        public_player_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=base/'width-authoring-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-width-authoring-latest.json').write_bytes(destination.read_bytes())
    print('PARTIAL;2040-field upper route prefix cold WRAM verified; full route/modes/windows open',flush=True)


if __name__=='__main__':main()
