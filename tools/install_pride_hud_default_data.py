"""Upgrade a verified unchanged local installation, retaining its previous manifest."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out = ROOT/'build/pride-hud-default-install'; out.mkdir()
    data = ROOT/'game-data'
    first = json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
    assert set(first) == {'schema', 'prepared_utc', 'original_payloads_retained', 'roms', 'scene_cache', 'player_sha256'}
    assert all(digest(data/spec['file']) == spec['sha256'] for spec in first['roms'].values())
    prepared = ROOT/'build/pride-hud-fresh43/setup-verification/Data & installed assets'
    expected = json.loads((prepared/'install.json').read_text())
    assert digest(data/first['scene_cache']['file']) == expected['scene_cache']['sha256']
    for key in ('menu_assets', 'native_final_assets', 'title_bank_assets', 'hud_assets'):
        target = data/expected[key]['file']
        assert not target.exists() or digest(target) == expected[key]['sha256'], ('preserve differing local resource', target)
    # The installation metadata changes deliberately; retain its exact old bytes
    # so older evidence remains resolvable. Imported data/settings stay in place.
    baseline = ROOT/'build/pride-hud-default-install-baseline'; baseline.mkdir()
    names = ['tools/pride_arena_history.py', 'game-data/install.json']
    if (data/'setup-last.log').exists(): names.append('game-data/setup-last.log')
    historical = {}
    for name in names:
        path = ROOT/name; archived = baseline/name.replace('/', '__')
        archived.write_bytes(path.read_bytes())
        historical[name] = dict(sha256=digest(path), archive=archived.relative_to(ROOT).as_posix())
    (baseline/'report.json').write_text(json.dumps(dict(historical_sources=historical), indent=2)+'\n')
    history = ROOT/'tools/pride_arena_history.py'
    text = history.read_text(); anchor = "    folders.append('pride-hud-preview-verifier-baseline')"
    assert text.count(anchor) == 1
    history.write_text(text.replace(anchor, anchor+"\n    folders.append('pride-hud-default-install-baseline')"))
    protected = {p.relative_to(ROOT).as_posix(): digest(p) for p in (ROOT/'settings').rglob('*') if p.is_file()}
    for p in (ROOT/'Lion King, The (USA).sfc', ROOT/'Lion King, The (World).md', data/'scenes-v1.cache',
              data/first['roms']['snes']['file'], data/first['roms']['megadrive']['file']):
        protected[p.relative_to(ROOT).as_posix()] = digest(p)
    cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT/'scripts/Setup.ps1'),
           '-SnesRom', str(ROOT/'Lion King, The (USA).sfc'), '-MdRom', str(ROOT/'Lion King, The (World).md'),
           '-NonInteractive']
    with (out/'setup.log').open('wb') as log:
        rc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=180,
                            creationflags=subprocess.CREATE_NO_WINDOW).returncode
    actual = json.loads((data/'install.json').read_text())
    checks = dict(actual_setup_succeeded=rc == 0,
                  existing_roms_cache_settings_and_saves_preserved=all(digest(ROOT/p) == sha for p, sha in protected.items()),
                  prepared_descriptors_match_tested_installation=all(actual[k] == expected[k] for k in
                    ('roms', 'scene_cache', 'menu_assets', 'native_final_assets', 'title_bank_assets', 'hud_assets')),
                  all_prepared_files_match_manifest=all(digest(data/actual[k]['file']) == actual[k]['sha256']
                    for k in ('scene_cache', 'menu_assets', 'native_final_assets', 'title_bank_assets', 'hud_assets')))
    paths = [Path(__file__), ROOT/'scripts/Setup.ps1', data/'install.json', baseline/'report.json']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=cmd,
                  previous_metadata_archived=True, preserved_files_sha256=protected,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()
