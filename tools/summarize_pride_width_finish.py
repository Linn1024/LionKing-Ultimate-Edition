"""Bind the narrow-view completion and reviewed boss/card save evidence."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import pixels


def main():
    paths = [Path(__file__)]
    prior_path = ROOT / 'build/pride-width-latest.json'
    prior = bound(prior_path)
    assert prior['result'] == 'PARTIAL' and prior['new_checks'] == 85
    paths.append(prior_path)
    builds = []
    for number in (3, 4, 5):
        folder = ROOT / f'build/pride-rng-player{number}'
        path = folder / 'build-report.json'
        report = bound(path)
        assert report['result'] == 'BUILT'
        assert digest(folder / 'player.exe') == report['binary_sha256']
        for name, sha in report['link_inputs_sha256'].items():
            assert digest(ROOT / name) == sha, name
        for name, sha in report['production_sha256'].items():
            assert digest(ROOT / name) == sha, name
        paths.extend([path, folder / 'player.exe', folder / 'save-compatibility.json'])
        builds.append(report)
    core = lambda r: {k: v for k, v in r['link_inputs_sha256'].items() if not k.endswith('/host.obj')}
    assert core(builds[0]) == core(builds[1]) == core(builds[2])
    contracts = [(ROOT / f'build/pride-rng-player{n}/save-compatibility.json').read_bytes() for n in (3, 4, 5)]
    assert contracts[0] == contracts[1] == contracts[2]
    checks = fields = 0
    reports = {}
    for relative, count in (
        ('pride-rng-player4/boss-saves', 37),
        ('pride-rng-player4/boss-slots', 8),
        ('pride-rng-player4/width-completion', 21),
        ('pride-rng-player5/card-saves', 47),
        ('pride-rng-player5/card-slots', 8),
    ):
        path = ROOT / 'build' / relative / 'report.json'
        r = bound(path)
        assert r['result'] == 'PASS' and len(r['checks']) == count and all(r['checks'].values()), relative
        checks += count
        fields += r.get('compared_fields', r.get('native_fields_compared', 0))
        paths.append(path)
        reports[relative] = r
    completion = reports['pride-rng-player4/width-completion']
    assert completion['normal_rng_on_256_completion_verified']
    assert completion['ordinary_poweron_controller_inputs_only']
    assert not completion['loaded_states'] and not completion['practice_or_guest_edits']
    assert completion['first_next_level_field'] == 3450 and completion['compared_fields'] == 4500
    for relative, field in (('pride-rng-player4/boss-slots', 2800), ('pride-rng-player5/card-slots', 3000)):
        assert reports[relative]['saved_field'] == field
    # Explicitly bind the real clients inspected during review. The card-slot
    # client is a native black transition with a loaded-slot notification.
    for relative in ('pride-rng-player4/boss-slots/live/client.png',
                     'pride-rng-player5/card-slots/live/client.png',
                     'pride-rng-player4/width-completion/aot/window.png',
                     'pride-rng-player5/card-saves/new-resume-aot/window.png'):
        path = ROOT / 'build' / relative
        assert pixels(path)[:2] == (512, 448), relative
        paths.append(path)
    preview = ROOT / 'dist/development-preview/LionKing.exe'
    assert digest(preview) == digest(ROOT / 'build/pride-launch2/player.exe')
    paths.append(preview)
    result = dict(result='PARTIAL', new_checks=checks, compared_fields=fields,
                  preceding_width_checks=85, preceding_rng_checks=129,
                  normal_rng_on_256_completion_verified=True, first_next_level_field=3450,
                  ordinary_boss_and_native_card_saves_verified=True,
                  tested_cross_build_save_contract_unchanged=True,
                  preceding_nonhost_link_inputs_unchanged=True,
                  native_card_md_rendering_enabled=False, busy_cache_saves_verified=False,
                  production_private_runtime_consolidated=False,
                  public_preview_unchanged=True, full_first_level_fidelity_complete=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    destination = ROOT / 'build/pride-rng-player5/width-finish-report.json'
    assert not destination.exists()
    destination.write_text(json.dumps(result, indent=2) + '\n')
    (ROOT / 'build/pride-width-finish-latest.json').write_bytes(destination.read_bytes())
    print(f'PARTIAL {checks} new checks; {fields} compared fields; first-level scope remains open', flush=True)


if __name__ == '__main__':
    main()
