"""Compare regenerated hook/RNG units and prove optional hooks preserve native output."""
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base = ROOT / 'build/pride-owned-guest-generation'
    gp = base / 'generation-report.json'
    generated = bound(gp)
    out = base / 'verification'
    out.mkdir()
    old_path = ROOT / 'build/pride-spawn-revival/generation-report.json'
    old = bound(old_path)
    checks = {}
    for name, sha in old['generated_sha256'].items():
        checks[name + '/all_source_bytes'] = digest(base / 'hooks' / name) == sha
    predecessor = ROOT / 'build/pride-rng-player/generated'
    names = sorted(p.name for p in (base / 'rng').glob('bank*.c'))
    checks['all_137_rng_generation_units'] = len(names) == 137 and all(
        (base / 'rng' / name).read_bytes() == (predecessor / name).read_bytes() for name in names)
    control = base / 'native-control'
    assert not control.exists()
    command = generated['commands']['hooks'].copy()
    command[command.index('--out-dir') + 1] = str(control)
    env = dict(os.environ, TLK_COMPILED_HOOK_POINTS='[]')
    with (out / 'native-generation.log').open('wb') as log:
        subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    native = sorted(p.name for p in control.glob('bank*.c'))
    checks['hooks_disabled_all_native_units'] = len(native) == 137 and all(
        (control / name).read_bytes() == (ROOT / 'engine/generated/snesrecomp' / name).read_bytes() for name in native)
    checks['hooks_disabled_no_bridge_calls'] = not any('PrideSceneCompiledPreOpcode' in (control / name).read_text() for name in native)
    checks['same_native_analysis_manifest'] = json.loads((control / 'program_manifest.json').read_text()) == json.loads(
        (ROOT / 'engine/generated/snesrecomp/program_manifest.json').read_text())
    paths = [Path(__file__), gp, old_path, ROOT / 'build/pride-rng-player/generation-report.json']
    for folder, unit_names in ((predecessor, names), (control, native), (ROOT / 'engine/generated/snesrecomp', native)):
        paths += [folder / name for name in unit_names]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, command=command,
                  native_units_compared=137, rng_units_compared=137, hook_units_compared=13,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={'native-generation.log': digest(out / 'native-generation.log')},
                  canonical_config_or_generated_tree_modified=False, full_first_level_fidelity_complete=False)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], [key for key, value in checks.items() if not value], flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()
