"""Bind loaded practice readiness and unchanged mixed-player presentation evidence."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-cli-practice';build_path=base/'build-report.json';build=bound(build_path)
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for variant,r in build['runs'].items():
        assert digest(base/(variant+'.exe'))==r['binary_sha256']
        for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    cache_path=ROOT/'build/pride-reset-cache-latest.json';cache=bound(cache_path);assert cache['result']=='PARTIAL'
    paths=[Path(__file__),build_path,cache_path];reports={};passed=0;fields=0
    for case in ('native','md'):
        path=base/case/'report.json';r=bound(path);assert r['result']=='PASS' and all(r['checks'].values())
        assert r['binaries_sha256']=={v:b['binary_sha256'] for v,b in build['runs'].items()}
        for variant in ('before','after'):
            for kind in ('ordinary','owned'):
                observation=r['observations'][variant+'/'+kind]
                assert observation['state'] in ((1,2) if variant=='after' else (0,))
                if variant=='after':fields+=3000-observation['field']
        passed+=len(r['checks']);paths.append(path);reports[case]=digest(path)
        prior_path=base/case/'prior/report.json';prior=bound(prior_path)
        assert prior['result']=='PASS' and all(prior['checks'].values())
        assert prior['candidate_binary_sha256']==build['runs']['before']['binary_sha256']
        passed+=len(prior['checks']);paths.append(prior_path);reports[case+'/prior']=digest(prior_path)
    result=dict(result='PARTIAL',checks_passed=passed,reports_sha256=reports,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                cli_practice_loaded_cases=4,replayed_native_fields=fields,all_native_video_and_wram_exact=True,
                complete_pcm_and_audio_stems_exact=True,prior_player_cold_cases=2,
                actual_windows_inspected=True,complete_practice_panel_pixel_oracle=False,
                private_machine_reset_while_owned_verified=False,legacy_save_migration_verified=False,
                public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-cli-practice-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL CLI practice:',passed,'checks;',fields,'loaded fields',flush=True)


if __name__=='__main__':main()
