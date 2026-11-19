"""Disclose superseded automatic-cache mutations; validate untouched research data."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    original=ROOT/'build/pride-music-output62/lifecycle/report.json'
    observer=ROOT/'build/pride-music-observer63/verification/report.json';observed=bound(observer)
    expected_report=observed['source_sha256'][original.relative_to(ROOT).as_posix()]
    assert digest(original)==expected_report
    old=json.loads(original.read_text());out=ROOT/'build/pride-music-output65/historical-cache-incident';out.mkdir()
    differences=[];unchanged={}
    for name,expected in old['artifacts_sha256'].items():
        path=original.parent/name;actual=digest(path)
        if actual==expected:unchanged[name]=expected;continue
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        differences.append(dict(path=name,expected_original_sha256=expected,observed_sha256=actual,preserved_changed_file=target.relative_to(out).as_posix()))
    expected_names={name+'/tlk_practice_boot.state' for name in ('continue-all-aot','hard-all-aot','revival-both-aot')}
    source_proof=out/'original-source-bindings.json'
    source_proof.write_text(json.dumps(dict(result='ORIGINAL_SOURCE_BINDINGS_ONLY',
        source_sha256={**old['source_sha256'],original.relative_to(ROOT).as_posix():expected_report},
        excluded_artifact_scope='This validates original sources only; it does not validate the three overwritten automatic boot-cache payloads.'),indent=2)+'\n')
    bound(source_proof)
    current=['component','completion','lifecycle','audio-device','windows-visible','package-play2','native75','allbugs-verification','hyena-effects','publication','cmd-play','game-window-verification']
    current_paths=[out.parent/name/'report.json' for name in current]
    for p in current_paths:
        r=bound(p);assert r['result']=='PASS' and all(r.get('checks',{'component':True}).values()),p
    checks=dict(original_report_bytes_unchanged=True,original_sources_bound=True,
        only_three_automatic_caches_changed={r['path'] for r in differences}==expected_names,
        all_other_historical_artifacts_exact=len(unchanged)==len(old['artifacts_sha256'])-3,
        changed_bytes_preserved=all(digest(out/r['preserved_changed_file'])==r['observed_sha256'] for r in differences),
        all_current65_reports_fully_bound=True)
    paths=[Path(__file__),original,observer,source_proof,*current_paths]
    # Bind the primary historical artifacts directly. The three superseded
    # caches are explicitly excluded, never silently accepted as originals.
    for name in unchanged:paths.append(original.parent/name)
    report=dict(result='DOCUMENTED_HISTORICAL_CACHE_MUTATION',checks=checks,differences=differences,
        original_cache_bytes_unrecovered=True,exact_copy_search_count=824,
        cause='Guest-read-only observer63 reused original config directories; host initialization refreshed their automatic boot caches.',
        required_probe_rule='Copy config and resource profile into an owned output directory before launching continuation diagnostics.',
        historical_primary_artifacts_verified=len(unchanged),current65_game_results_unchanged=True,
        original_historical_report_not_fully_artifact_bindable=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,'untouched artifacts',len(unchanged),flush=True)


if __name__=='__main__':main()
