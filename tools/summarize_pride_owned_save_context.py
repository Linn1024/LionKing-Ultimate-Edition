"""Bind the owned idle-save rule and its real Windows replay checks."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-rng-player7'
    preceding = ROOT / 'build/pride-width-finish-latest.json'
    prior = bound(preceding)
    assert prior['result'] == 'PARTIAL' and prior['new_checks'] == 121
    paths = [Path(__file__), preceding]
    builds = []
    for folder in (ROOT / 'build/pride-rng-player5', base):
        path = folder / 'build-report.json'
        r = bound(path)
        assert r['result'] == 'BUILT' and digest(folder / 'player.exe') == r['binary_sha256']
        for name, sha in r['link_inputs_sha256'].items():
            assert digest(ROOT / name) == sha, name
        for name, sha in r['production_sha256'].items():
            assert digest(ROOT / name) == sha, name
        paths.append(path)
        builds.append(r)
    core = lambda r: {k: v for k, v in r['link_inputs_sha256'].items() if not k.endswith('/host.obj')}
    assert core(builds[0]) == core(builds[1])
    assert (base / 'save-compatibility.json').read_bytes() == (ROOT / 'build/pride-rng-player5/save-compatibility.json').read_bytes()
    checks = fields = 0
    for name, count, nfields in (('boss-saves', 37, 6800), ('card-saves', 47, 18000)):
        p = base / name / 'report.json'
        r = bound(p)
        assert r['result'] == 'PASS' and len(r['checks']) == count and all(r['checks'].values())
        assert r['compared_fields'] == nfields
        paths.append(p)
        checks += count
        fields += nfields
    path = base / 'eligibility-equivalence/report.json'
    r = bound(path)
    assert r['result'] == 'PASS' and r['compared_contexts'] == 245760 and r['null_context_rejected']
    paths.extend([path, ROOT / 'engine/runner/tlk_pride_save_context.h'])
    preview = ROOT / 'dist/development-preview/LionKing.exe'
    assert digest(preview) == digest(ROOT / 'build/pride-launch2/player.exe')
    paths.append(preview)
    report = dict(result='PARTIAL', new_checks=checks, compared_fields=fields,
                  compared_eligibility_contexts=245760, null_context_rejected=True,
                  preceding_width_finish_checks=121, all_nonhost_link_inputs_unchanged=True,
                  reviewed_eligibility_in_owned_engine_header=True,
                  whole_private_runtime_production_consolidated=False,
                  busy_cache_serialization_implemented=False, public_preview_unchanged=True,
                  full_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    destination = base / 'owned-save-context-report.json'
    assert not destination.exists()
    destination.write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'build/pride-owned-save-context-latest.json').write_bytes(destination.read_bytes())
    print(f'PARTIAL {checks} real replay checks; {fields} fields; 245760 eligibility contexts', flush=True)


if __name__ == '__main__':
    main()
