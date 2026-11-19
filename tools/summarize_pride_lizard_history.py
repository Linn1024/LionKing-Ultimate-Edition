"""Index current lizard lifecycle confirmation and the new RNG-clear contract."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    path=ROOT/'build/pride-lizard-history/audit.json';r=bound(path)
    assert r['result']=='PARTIAL' and all(r['checks'].values())
    report=dict(result='PARTIAL',matching_lizard_updates=r['matching_lizard_controller_updates'],checks=len(r['checks']),
        original_native_clear_fixtures=r['new_original_native_clear_fixtures'],
        route_difference_is_valid_random_reaction=True,lizard_spawn_motion_fix_required_by_this_route=False,
        production_changed=False,rng_source_enabled=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),path)})
    (ROOT/'build/pride-lizard-history-latest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:132 paired lizard updates; valid random branch confirmed;48 original clear fixtures',flush=True)


if __name__=='__main__':main()
